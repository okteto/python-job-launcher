import os
from datetime import datetime
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException

def getDevAffinity():
  # we set affinity to ensure that the job is placed in the same host as the volume
  return client.V1Affinity(
      pod_affinity=client.V1PodAffinity(
        required_during_scheduling_ignored_during_execution=[
          client.V1PodAffinityTerm(
            label_selector=client.V1LabelSelector(
              match_labels=dict({"interactive.dev.okteto.com": "python-job-launcher"}),
            ),
            topology_key="kubernetes.io/hostname",
          ),
        ],
      ),
    )

def getDevVolume():
  name = "okteto-{name}".format(name=os.environ["OKTETO_NAME"])
  volume_mount = client.V1VolumeMount(
    name=name,
    mount_path="/app",
    # the code is always mounted on the 'src' directory of the dev volume
    # in this case, we only want the job folder
    sub_path="src/job"
  )

  claim = client.V1PersistentVolumeClaimVolumeSource(claim_name=name)
  volume = client.V1Volume(name=name, persistent_volume_claim=claim)
  
  return volume, volume_mount


if __name__ == "__main__":
  with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as file:
    namespace = file.read()

  config.load_incluster_config()
  api = client.BatchV1Api()

  now = int(datetime.utcnow().timestamp())
  job_name = "hello-world-job-{now}".format(now=now)

  affinity = None  
  volumes = []
  volume_mounts = []

  # include the volume created by okteto if we are running in dev mode
  if os.environ['ENV'] == "dev":
    volume, mount = getDevVolume()
    volumes.append(volume)    
    volume_mounts.append(mount)
    affinity = getDevAffinity()

  container = client.V1Container(
    name=job_name, 
    image="okteto/python-job-launcher:job", 
    volume_mounts=volume_mounts, 
    image_pull_policy="Always")

  template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "job-launcher"}),
            spec=client.V1PodSpec(
              affinity=affinity,
              restart_policy="Never", 
              containers=[container],
              volumes=volumes))

  spec = client.V1JobSpec(
            template=template,
            backoff_limit=3,
            ttl_seconds_after_finished=60)
  
  job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=spec)

  try: 
    api_response = api.create_namespaced_job(
        namespace=namespace,
        body=job)
    print("launched {job}: {status}".format(job=job_name, status=api_response.status))
  except ApiException as e:
    print(e) # Handle the exception.

  