# Dependency-Track service template

At Gate G13, fetch the current official Dependency-Track Docker Compose definition from `https://dependencytrack.org/docker-compose.yml`, review it, pin every image to an immutable digest, store the reviewed generated copy under `.sai-quality/generated/dependency-track/`, and record the source hash in evidence. Do not commit default/admin credentials.
