import sys, os
from os import path
from typing import Dict, Optional
import yaml
import traceback
import subprocess

from modelbit.ux import SHELL_FORMAT_FUNCS
from modelbit.api import MbApi
from modelbit.error import UserFacingError
from modelbit.api.metadata_api import MetadataApi, MetadataValidationResponse


def getRepoRoot() -> Optional[str]:
  (exitCode, repoRoot) = subprocess.getstatusoutput('git rev-parse --show-toplevel')
  if exitCode != 0:
    return None
  return repoRoot


def writePreCommitHook():
  try:
    repoRoot = getRepoRoot()
    if repoRoot is None:
      raise Exception(f"Could not find repository near {os.getcwd()}")
    hookPath = os.path.join(repoRoot, ".git/hooks/pre-commit")
    with open(hookPath, "w") as f:
      f.write("""#!/bin/sh

exec modelbit validate
""")
    os.chmod(hookPath, 0o775)
  except Exception as err:
    print(f"Unable to write pre-commit hook: {err}", file=sys.stderr)


def show(message: str):
  print(message, file=sys.stderr)


def _red(message: str) -> str:
  return SHELL_FORMAT_FUNCS["red"](message)


def _purple(message: str) -> str:
  return SHELL_FORMAT_FUNCS["purple"](message)


def validateRepo(mbApi: MbApi, dir: str) -> bool:
  try:
    return validateDeployments(mbApi, dir)
  except UserFacingError as err:  # intentional errors to block shipping
    show(_red("Validation error: ") + str(err))
    return False
  except Exception as err:  # bugs that'll block deployments so let them through
    show(_red("Unexpected error: ") + str(err))
    show(traceback.format_exc())
    return True


def validateDeployments(mbApi: MbApi, dir: str) -> bool:
  depsPath = path.join(dir, "deployments")
  validationsPassed: bool = True

  if not path.exists(depsPath):
    raise ValueError(f"Unable to read deployments directory '{depsPath}'")

  allDeploymentNames = sorted(os.listdir(depsPath))
  if len(allDeploymentNames) == 0:
    return validationsPassed

  show("\nValidating deployments...")
  metadataValidations = validateMetadataFiles(mbApi, depsPath)
  for d in allDeploymentNames:
    if not path.isdir(path.join(depsPath, d)):
      continue
    passed = validateOneDeployment(depsPath,
                                   d,
                                   metadataValidationError=metadataValidations.getError(
                                       path.join(depsPath, d, "metadata.yaml")))
    validationsPassed = validationsPassed and passed
  show("")
  return validationsPassed


def validateOneDeployment(depsPath: str, depName: str, metadataValidationError: Optional[str]) -> bool:

  def pathExists(fileName: str):
    return path.exists(path.join(depsPath, depName, fileName))

  if pathExists(".archived"):
    return True  # don't validate archived deployments

  mainFuncError: Optional[str] = getMainFuncError(path.join(depsPath, depName))

  if not pathExists("source.py") and not pathExists("jobs.yaml"):
    show(f"  ❌ {_red(depName)}: Missing {_purple('source.py')}")
    return False
  elif not pathExists("metadata.yaml"):
    show(f"  ❌ {_red(depName)}: Missing {_purple('metadata.yaml')}")
    return False
  elif metadataValidationError:
    show(f"  ❌ {_red(depName)}: Error in {_purple('metadata.yaml')}:" + f" {metadataValidationError}")
    return False
  elif mainFuncError:
    show(f"  ❌ {_red(depName)}: Error in {_purple('metadata.yaml')}:" + f" {mainFuncError}")
    return False
  else:
    show(f"  ✅ {depName}")
    return True


# returns filePath -> fileContents. Getting them all so they can be in one web request
def collectMetadataFiles(depsPath: str) -> Dict[str, str]:
  files: Dict[str, str] = {}
  for d in os.listdir(depsPath):
    filePath = path.join(depsPath, d, "metadata.yaml")
    if path.exists(filePath):
      with open(filePath) as f:
        files[filePath] = f.read()
  return files


# returns path -> Optional[errorMessage]
def validateMetadataFiles(mbApi: MbApi, depsPath: str) -> MetadataValidationResponse:
  files = collectMetadataFiles(depsPath)
  return MetadataApi(mbApi).validateMetadataFiles(files)


def getMainFuncError(depPath: str) -> Optional[str]:
  try:
    with open(path.join(depPath, "metadata.yaml")) as f:
      obj = yaml.safe_load(f)
      mainFunc = obj["runtimeInfo"].get("mainFunction")
    with open(path.join(depPath, "source.py")) as f:
      sourceCode = f.read()
      if mainFunc is None:
        return f"The mainFunction parameter is missing from metadata.yaml"
      if mainFunc not in sourceCode:
        return f"The mainFunction '{mainFunc}' was not found in source.py"
  except:
    pass  # if something goes wrong in the parsing other validators would have caught it

  return None
