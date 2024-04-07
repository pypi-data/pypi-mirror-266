import docker

def build_docker_image(dockerfile_path, image_name, tag='latest'):
    client = docker.from_env()

    try:
        print(f"Building Docker image '{image_name}:{tag}'...")
        image, build_logs = client.images.build(
            path=dockerfile_path,
            tag=f"{image_name}:{tag}",
            rm=True,
            forcerm=True
        )
        print(f"Docker image '{image_name}:{tag}' built successfully.")
        return image.id
    except docker.errors.BuildError as e:
        print(f"Failed to build Docker image: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while building Docker image: {e}")
        return None