# Profiling por Stack

Leer cuando haya que perfilar CPU/memoria de un backend o buscar memory leaks. Elige la sección según el runtime del proyecto.

## Node.js / Express

```bash
# CPU profiling con clinic.js
npm install -g clinic
clinic flame -- node src/server.js   # Flamegraph de CPU
clinic doctor -- node src/server.js  # Diagnóstico completo
clinic bubbleprof -- node src/server.js  # Async analysis

# Built-in profiler
node --prof src/server.js
node --prof-process isolate-*.log > processed.txt

# Memory leaks
node --inspect src/server.js  # Conectar Chrome DevTools
```

**Patrones Node.js a buscar:**
- Event loop lag > 100ms → bloqueo síncrono en el thread principal
- `setInterval` sin `clearInterval` → memory leak garantizado
- Promises sin `.catch()` → unhandled rejections silenciosas
- `JSON.parse(JSON.stringify(obj))` en hot path → usar `structuredClone()`

## .NET 8

```bash
# CPU + Memory profiling
dotnet-trace collect --process-id <PID> --providers Microsoft-DotNETCore-SampleProfiler
dotnet-counters monitor --process-id <PID> System.Runtime

# Heap snapshot
dotnet-gcdump collect --process-id <PID>
dotnet-gcdump report gcdump_<PID>.gcdump

# Benchmark con BenchmarkDotNet
[MemoryDiagnoser]
[SimpleJob(RuntimeMoniker.Net80)]
public class MyBenchmark {
    [Benchmark] public void Method() { ... }
}
```

**Patrones .NET a buscar:**
- GC Gen2 collections frecuentes → objetos de larga vida innecesarios
- `async void` → exceptions no capturadas
- `Task.Result` o `.GetAwaiter().GetResult()` → deadlocks
- `HttpClient` instanciado en cada request → socket exhaustion

## Python / FastAPI

```bash
# CPU profiling
py-spy top --pid <PID>                    # Live sampling
py-spy record -o profile.svg --pid <PID> # Flamegraph

# Memory
memray run -o output.bin app.py
memray flamegraph output.bin

# FastAPI específico
# Usar slowapi para rate limiting y middleware de timing
```
