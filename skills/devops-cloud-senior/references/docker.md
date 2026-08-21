# Docker — Multi-stage Profesional

## Template .NET 8 optimizado

```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
COPY ["src/Telemetria.Identity.API/Telemetria.Identity.API.csproj", "src/Telemetria.Identity.API/"]
RUN dotnet restore "src/Telemetria.Identity.API/Telemetria.Identity.API.csproj"
COPY . .
RUN dotnet publish "src/Telemetria.Identity.API" -c Release -o /app/publish \
    --no-restore \
    /p:UseAppHost=false \
    /p:PublishTrimmed=false

# Runtime stage (sin SDK, imagen mínima)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
COPY --from=build /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ENTRYPOINT ["dotnet", "Telemetria.Identity.API.dll"]
```

## Template Node.js optimizado

```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS final
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S app && adduser -S app -G app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER app
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

## Reglas Docker siempre

- `.dockerignore` siempre presente (excluir node_modules, .git, *.md, tests)
- Imagen base específica con tag (`node:22-alpine`, no `node:latest`)
- Usuario no-root en runtime (`adduser appuser`)
- `HEALTHCHECK` en cada imagen de servicio
- Escanear con `trivy image` antes de push a registry
