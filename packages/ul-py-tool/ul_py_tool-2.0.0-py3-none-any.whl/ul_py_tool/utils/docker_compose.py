from typing import List, Dict, Union, Any, Optional, Tuple, Iterable

from pydantic import BaseModel

MAP_CHOICES_RESTART = {
    "Always": "always",
    "OnFailure": "on-failure",
    "Never": "no",
}
KUBERNETES_OBJECTS__TRANSFORM_TO_DCF__TYPE = ['Deployment', 'StatefulSet', 'Job']
KUBERNETES_OBJECTS__DEPENDS_ON_OBJECT__TYPE = ['StatefulSet']


class DockerComposeService(BaseModel):
    name: str
    kubernetes_type: str
    replicas: int
    image: Optional[str]
    restart: Optional[str]
    volumes: Optional[List[str]]
    ports: Optional[List[str]]
    expose: Optional[List[int]]
    command: Optional[List[str]]
    environment: Optional[Dict[str, Union[str, int]]]

    @staticmethod
    def from_kubernetes(yaml: Dict[str, Any]) -> Tuple['DockerComposeService', Dict[str, None]]:
        return DockerComposeService(
            name=yaml['metadata']["name"],
            kubernetes_type=yaml['kind'],
            image=yaml["spec"]["template"]["spec"]["containers"][0]["image"],
            restart=MAP_CHOICES_RESTART[yaml["spec"]["template"]["spec"].get("restartPolicy", "Always")],
            volumes=[f"{volume['name']}:{volume['mountPath']}" for volume in yaml["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]]
            if yaml["spec"]["template"]["spec"]["containers"][0].get("volumeMounts") is not None else [],
            environment={
                env['name']: env['value'] for env in yaml["spec"]["template"]["spec"]["containers"][0]["env"]
            } if yaml["spec"]["template"]["spec"]["containers"][0].get("env") is not None
            else {},
            command=yaml["spec"]["template"]["spec"]["containers"][0].get("command", []) + yaml["spec"]["template"]["spec"]["containers"][0].get("args", []),
            replicas=yaml["spec"].get("replicas", 1),
            expose=[
                r["containerPort"] for r in yaml["spec"]["template"]["spec"]["containers"][0].get("ports", [])
            ] if not yaml['metadata']["name"].endswith('balancer') else [],
            ports=[
                f'{r["containerPort"]}:{r["containerPort"]}' for r in yaml["spec"]["template"]["spec"]["containers"][0].get("ports", [])
            ] if yaml['metadata']["name"].endswith('balancer') else [],

        ), {volume['name']: None for volume in yaml["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]} if yaml["spec"]["template"]["spec"]["containers"][0].get("volumeMounts") is not None else {}

    def to_json(self, common_dependencies: List[str]) -> Dict[str, Any]:
        return {
            self.name: {
                "image": self.image,
                "restart": self.restart,
                "volumes": self.volumes,
                "deploy": {
                    "replicas": self.replicas,
                },
                "ports": self.ports,
                "expose": self.expose,
                "command": self.command,
                "environment": self.environment,
                "depends_on": common_dependencies,
            },
        } if self.replicas != 0 else {}


class DockerComposeFile(BaseModel):
    volumes: Dict[str, None]
    common_dependencies: List[str]
    version: str
    services: List[DockerComposeService]

    @staticmethod
    def from_kubernetes(file: Iterable[Dict[str, Any]]) -> 'DockerComposeFile':
        volumes_list: Dict[str, None] = {}
        services_list: List[DockerComposeService] = []
        common_dependencies: List[str] = []
        for resource in file:
            if resource['kind'] not in KUBERNETES_OBJECTS__TRANSFORM_TO_DCF__TYPE:
                continue
            service, volumes = DockerComposeService.from_kubernetes(resource)
            volumes_list.update(**volumes)
            services_list.append(service)
            if resource['kind'] in KUBERNETES_OBJECTS__DEPENDS_ON_OBJECT__TYPE:
                # No need in worker or api if no DB or broker exists
                common_dependencies.append(service.name)

        return DockerComposeFile(
            version="3.8",
            volumes=volumes_list,
            services=services_list,
            common_dependencies=common_dependencies,
        )

    def to_json(self) -> Dict[str, Any]:
        services_dict: Dict[str, Any] = {}
        for service in self.services:
            service_json = service.to_json(
                common_dependencies=self.common_dependencies if service.kubernetes_type not in KUBERNETES_OBJECTS__DEPENDS_ON_OBJECT__TYPE else [],
            )
            services_dict.update(**service_json)
        return {
            "version": "3.8",
            "volumes": self.volumes,
            "services": services_dict,
        }
