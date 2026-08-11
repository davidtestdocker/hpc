apiVersion: v1
kind: Service

metadata:
  name: nvidia-dcgm
  namespace: hpc-platform-dev

spec:
  selector:
    app: nvidia-dcgm

  ports:
    - name: dcgm
      port: 5555
      targetPort: 5555
