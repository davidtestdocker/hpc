apiVersion: argoproj.io/v1alpha1
kind: Application

metadata:
  name: hpc-stage
  namespace: argocd

spec:
  project: hpc-platform

  source:
    repoURL: https://github.com/davidtestdocker/hpc.git
    targetRevision: master
    path: kustomize/overlays/stage

  destination:
    server: https://kubernetes.default.svc
    namespace: hpc-platform-stage

  syncPolicy:
    automated:
      prune: true
      selfHeal: true

    syncOptions:
      - CreateNamespace=true
