import argparse

from pyfunvice.docker_cli import build_docker_image


def main():
    parser = argparse.ArgumentParser(description="pyfunvice CLI")
    parser.add_argument("--image-name", required=True, help="Docker image name")
    parser.add_argument("--tag", default="latest", help="Docker image tag")
    parser.add_argument("--dockerfile", help="Path to custom Dockerfile")

    args = parser.parse_args()

    image_name = args.image_name
    tag = args.tag
    dockerfile_path = args.dockerfile

    if dockerfile_path:
        with open(dockerfile_path, "r") as file:
            dockerfile_content = file.read()
        image_id = build_docker_image(
            image_name, tag, dockerfile_content=dockerfile_content
        )
    else:
        image_id = build_docker_image(image_name, tag)

    if image_id:
        print(f"Docker image built successfully. Image ID: {image_id}")
    else:
        print("Failed to build Docker image.")
