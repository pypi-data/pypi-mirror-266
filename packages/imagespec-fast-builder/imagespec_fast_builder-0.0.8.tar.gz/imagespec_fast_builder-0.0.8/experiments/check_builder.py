import argparse

from flytekit import ImageSpec

from flytekitplugins.envd import EnvdImageSpecBuilder
from imagespec_fast_builder import FastImageBuilder

image_spec = ImageSpec(
    name="flyte_playground",
    packages=["numpy"],
    # conda_packages=["numpy"],
    # cuda="12",
    # cudnn="8",
    # registry="localhost:30000",
)

parser = argparse.ArgumentParser()
parser.add_argument("builder", choices=["envd", "fast-builder"])

args = parser.parse_args()

if args.builder == "envd":
    builder = EnvdImageSpecBuilder()
else:
    builder = FastImageBuilder()

builder.build_image(image_spec)
