# Azure Container Apps (FleetVision)

## Bicep pattern para microservicio

```bicep
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'fv-identity'
  location: location
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      secrets: [
        { name: 'db-connection', keyVaultUrl: dbSecretUri, identity: 'system' }
      ]
      ingress: {
        external: false
        targetPort: 8080
        transport: 'http2'
      }
      registries: [{ server: acrName, identity: 'system' }]
    }
    template: {
      scale: { minReplicas: 1, maxReplicas: 10
        rules: [{ name: 'http-scaling', http: { metadata: { concurrentRequests: '100' } } }]
      }
      containers: [{
        name: 'identity'
        image: '${acrName}.azurecr.io/fv-identity:${imageTag}'
        resources: { cpu: json('0.5'), memory: '1Gi' }
        env: [
          { name: 'ConnectionStrings__Default', secretRef: 'db-connection' }
          { name: 'ASPNETCORE_ENVIRONMENT', value: environment }
        ]
        probes: [
          { type: 'Liveness', httpGet: { path: '/health/live', port: 8080 } }
          { type: 'Readiness', httpGet: { path: '/health/ready', port: 8080 } }
        ]
      }]
    }
  }
}
```

## Checklist de deploy a Azure

- [ ] Imagen escaneada con Trivy (0 CVEs críticos)
- [ ] Secrets en Azure Key Vault (nunca en env vars directas)
- [ ] Managed Identity configurada (sin connection strings con passwords)
- [ ] Health checks `/health/live` y `/health/ready` implementados
- [ ] Scale rules definidas (HTTP-based scaling)
- [ ] Revision labels para blue/green (`--revision-suffix v${BUILD_NUMBER}`)
- [ ] Traffic split para canary: `--traffic fv-identity-v2=10 fv-identity-v1=90`
- [ ] Alertas configuradas en Azure Monitor
