from smol_k8s_lab.k8s_tools.argocd_util import (install_with_argocd,
                                                check_if_argocd_app_exists)
from smol_k8s_lab.k8s_tools.k8s_lib import K8s


def configure_longhorn(k8s_obj: K8s, config: dict) -> None:
    """
    setup the longhorn operator as an Argo CD Application
    """
    # check if minio is using smol_k8s_lab init and if already present in Argo CD
    if not check_if_argocd_app_exists('longhorn'):
        # actual installation of the minio app
        install_with_argocd(k8s_obj, 'longhorn', config['argo'])
