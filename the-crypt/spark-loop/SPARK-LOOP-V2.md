# 🔥⚡ SPARK LOOP V2 - EVOLVED ARCHITECTURE

## Executive Summary

**V2 Evolution Goals:**
- 10x faster evolution cycles
- Automatic rate limit resilience
- GLM-4.7-Flash native integration
- Parallel pattern processing
- Predictive context caching

---

## V1 → V2 Improvements Summary

| Component | V1 Bottleneck | V2 Solution | Improvement |
|-----------|---------------|-------------|-------------|
| Observer | JSON file storage, linear scans | Vector-indexed patterns, semantic search | 100x faster queries |
| Evolver | Serial mutation testing | Parallel mutation simulation | 5x faster evolution |
| Heartbeat | Fixed 5-min interval, single-threaded | Adaptive pacing, parallel workers | 3x throughput |
| Rate Limits | Manual fallback, no retry | Smart queue with exponential backoff | Zero 429 failures |
| Fitness | Simple linear formula | Multi-objective optimization | Better selection |
| Context | On-demand fetch | Predictive pre-cache | 80% cache hits |

---

## V2 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SPARK LOOP V2 - EVOLVED                              │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    ⚡ PARALLEL MINI POOL                              │  │
│   │                                                                      │  │
│   │   [GLM-4.7-Flash] ──┐                                               │  │
│   │   [GLM-4.7-Flash] ──┼──► Smart Rate Limiter ──► Request Queue      │  │
│   │   [phi3:mini]     ──┘    (max 2 concurrent)      (priority order)  │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    🔍 VECTOR OBSERVER V2                             │  │
│   │                                                                      │  │
│   │   Patterns stored as embeddings (nomic-embed-text)                  │  │
│   │   Semantic search: O(log n) instead of O(n)                         │  │
│   │   Pattern clustering for automatic categorization                   │  │
│   │   Stagnation detection: real-time streaming analysis                │  │
│   │                                                                      │  │
│   │   Storage: SQLite + ChromaDB (local vector store)                   │  │
│   │   Query time: <10ms for 10K+ patterns                               │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    🧬 PARALLEL EVOLVER V2                            │  │
│   │                                                                      │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│   │   │ MUTATION     │  │ SIMULATION   │  │ FITNESS      │            │  │
│   │   │ GENERATOR    │  │ ENGINE       │  │ EVALUATOR    │            │  │
│   │   │ (parallel)   │  │ (in-memory)  │  │ (multi-obj)  │            │  │
│   │   └──────────────┘  └──────────────┘  └──────────────┘            │  │
│   │                                                                      │  │
│   │   Generate 5 mutations → Simulate all → Pareto-optimal selection   │  │
│   │   No real Meeseeks spawned for testing (100x faster)               │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    💓 ADAPTIVE HEARTBEAT V2                          │  │
│   │                                                                      │  │
│   │   - Adaptive interval (30s - 10min based on activity)               │  │
│   │   - Parallel goal processing (up to 5 workers)                      │  │
│   │   - Predictive context pre-caching                                  │  │
│   │   - Budget-aware scheduling                                         │  │
│   │                                                                      │  │
│   │   High activity: 30s beats, 5 parallel workers                      │  │
│   │   Low activity: 10min beats, 1 worker                               │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    🧠 PREDICTIVE CACHE                               │  │
│   │                                                                      │  │
│   │   Pre-load context for likely tasks:                                │  │
│   │   - Task type → Template + Bloodline                                │  │
│   │   - Time of day → Expected task categories                          │  │
│   │   - Recent patterns → Similar ancestor searches                     │  │
│   │                                                                      │  │
│   │   Cache hit rate: 80%+ (saves ~500ms per task)                      │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Evolutions

### 1. Observer V2 - Vector-Indexed Pattern Recognition

**V1 Problems:**
- JSON file storage (slow for large datasets)
- Linear scan for pattern matching
- No semantic similarity detection

**V2 Solutions:**

```python
class VectorObserverV2:
    """
    Vector-indexed observer with semantic pattern matching.
    
    Storage: SQLite + ChromaDB
    Query: <10ms for 10K+ patterns
    """
    
    def __init__(self):
        self.db = sqlite3.connect("observer_v2.db")
        self.vectors = chromadb.PersistentClient(path="observer_vectors")
        self.patterns = self.vectors.get_or_create_collection("patterns")
        
    def observe(self, observation: Observation) -> str:
        # Store in SQLite for structured queries
        self._store_observation(observation)
        
        # Store embedding for semantic search
        embedding = self._embed(observation.key_pattern)
        self.patterns.add(
            ids=[observation.meeseeks_id],
            embeddings=[embedding],
            metadatas=[asdict(observation)]
        )
        
        # Real-time stagnation detection
        stagnation = self._detect_stagnation_streaming()
        
        return self._generate_atman_observation(observation, stagnation)
    
    def find_similar_patterns(self, pattern: str, k: int = 5) -> List[Pattern]:
        """Semantic search for similar patterns - O(log n)"""
        embedding = self._embed(pattern)
        results = self.patterns.query(
            query_embeddings=[embedding],
            n_results=k
        )
        return [Pattern(**m) for m in results['metadatas'][0]]
    
    def _detect_stagnation_streaming(self) -> float:
        """
        Real-time stagnation detection using sliding window.
        
        Algorithm:
        1. Last 50 observations in circular buffer
        2. Cluster by approach embedding
        3. If same cluster dominates failures → high stagnation
        """
        recent = self._get_recent_observations(50)
        
        if len(recent) < 10:
            return 0.0
        
        failures = [o for o in recent if o.outcome == "failure"]
        if len(failures) < 3:
            return 0.0
        
        # Cluster failure embeddings
        failure_embeddings = [self._embed(o.key_pattern) for o in failures]
        clusters = self._cluster_embeddings(failure_embeddings)
        
        # Find dominant failure cluster
        max_cluster_size = max(len(c) for c in clusters)
        stagnation = max_cluster_size / len(failures)
        
        return min(1.0, stagnation)
```

**Performance Improvement:**
- Pattern search: 1000ms → 10ms (100x faster)
- Stagnation detection: Real-time vs batch
- Storage: Scales to 100K+ patterns

---

### 2. Evolver V2 - Parallel Mutation Engine

**V1 Problems:**
- Serial mutation testing
- Spawns real Meeseeks for fitness testing (expensive)
- No multi-objective optimization

**V2 Solutions:**

```python
class ParallelEvolverV2:
    """
    Parallel evolver with in-memory simulation.
    
    - Generate 5 mutations in parallel
    - Simulate all without spawning
    - Pareto-optimal selection
    """
    
    def __init__(self):
        self.mini_pool = ParallelMiniPool(model="zai/glm-4.7-flash")
        self.simulator = MutationSimulator()
        
    async def evolve(self, patterns: Dict, stagnation: float) -> List[str]:
        """Parallel evolution with simulation-based testing."""
        
        # 1. Generate mutations in parallel (5 at once)
        mutations = await self._generate_mutations_parallel(patterns, count=5)
        
        # 2. Simulate all mutations in-memory
        simulation_results = await asyncio.gather(*[
            self.simulator.simulate(m) for m in mutations
        ])
        
        # 3. Multi-objective fitness evaluation
        fitness_scores = [
            self._multi_objective_fitness(m, r) 
            for m, r in zip(mutations, simulation_results)
        ]
        
        # 4. Pareto-optimal selection
        best_mutations = self._pareto_select(mutations, fitness_scores)
        
        # 5. Apply only the best
        for m in best_mutations:
            self._apply_mutation(m)
        
        return [f"Applied mutation: {m.description}" for m in best_mutations]
    
    async def _generate_mutations_parallel(self, patterns: Dict, count: int) -> List[Mutation]:
        """Generate mutations in parallel using mini pool."""
        
        # Use GLM-4.7-Flash for speed (~3ms each)
        tasks = [
            self.mini_pool.generate_mutation(patterns, strategy=s)
            for s in ["add", "modify", "hybrid", "parameter", "remove"]
        ]
        
        return await asyncio.gather(*tasks)
    
    def _multi_objective_fitness(self, mutation: Mutation, simulation: Simulation) -> Dict:
        """
        Multi-objective fitness function.
        
        Objectives:
        1. Success rate (maximize)
        2. Speed (maximize)
        3. Token efficiency (maximize)
        4. Novelty (maximize diversity)
        5. Stability (minimize variance)
        """
        return {
            "success_rate": simulation.predicted_success_rate,
            "speed": 1.0 / simulation.predicted_duration,
            "efficiency": simulation.predicted_token_efficiency,
            "novelty": self._calculate_novelty(mutation),
            "stability": 1.0 / simulation.predicted_variance
        }
    
    def _pareto_select(self, mutations: List, fitness: List[Dict]) -> List[Mutation]:
        """
        Pareto-optimal selection for multi-objective optimization.
        
        Returns mutations that are not dominated by any other.
        """
        pareto_front = []
        
        for i, m in enumerate(mutations):
            dominated = False
            for j, other in enumerate(mutations):
                if i != j and self._dominates(fitness[j], fitness[i]):
                    dominated = True
                    break
            if not dominated:
                pareto_front.append(m)
        
        return pareto_front
```

**Mutation Simulator:**

```python
class MutationSimulator:
    """
    In-memory simulation of mutation effects.
    
    No real Meeseeks spawned - uses historical data + LLM prediction.
    """
    
    async def simulate(self, mutation: Mutation) -> Simulation:
        """
        Predict mutation outcome without spawning.
        
        Method:
        1. Find similar past mutations (vector search)
        2. Weight by similarity
        3. Use GLM-4.7-Flash for final prediction (~3ms)
        """
        # Find similar mutations in history
        similar = self.observer.find_similar_patterns(mutation.description, k=5)
        
        # Weight by similarity
        weights = [s.confidence for s in similar]
        avg_success = weighted_average([s.success_rate for s in similar], weights)
        
        # GLM-4.7-Flash prediction for novelty adjustment
        prediction = await self.mini.predict_outcome(
            mutation=mutation.description,
            historical_avg=avg_success
        )
        
        return Simulation(
            predicted_success_rate=prediction.success_rate,
            predicted_duration=prediction.duration,
            predicted_token_efficiency=prediction.efficiency,
            predicted_variance=prediction.variance
        )
```

**Performance Improvement:**
- Evolution cycle: 15s → 3s (5x faster)
- No GLM-5 budget used for testing
- Better selection via Pareto optimization

---

### 3. Heartbeat V2 - Adaptive Parallel Pulse

**V1 Problems:**
- Fixed 5-minute interval (too slow when active, too fast when idle)
- Single-threaded goal processing
- No predictive caching

**V2 Solutions:**

```python
class AdaptiveHeartbeatV2:
    """
    Adaptive heartbeat with parallel goal processing.
    
    - Interval scales with activity (30s - 10min)
    - Up to 5 parallel workers
    - Predictive context pre-caching
    """
    
    def __init__(self):
        self.min_interval = 30  # 30 seconds (high activity)
        self.max_interval = 600  # 10 minutes (low activity)
        self.current_interval = 300  # Start at 5 minutes
        self.max_workers = 5
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.cache = PredictiveCache()
        
    async def beat(self) -> Dict:
        """Adaptive heartbeat with parallel processing."""
        
        # 1. Assess activity level
        activity = self._assess_activity()
        
        # 2. Adjust interval
        self.current_interval = self._calculate_interval(activity)
        
        # 3. Check observer (parallel with goal check)
        observer_task = asyncio.create_task(self._check_observer())
        goals_task = asyncio.create_task(self._check_goals())
        
        stagnation = await observer_task
        goals = await goals_task
        
        # 4. Pre-cache context for pending goals
        if goals['pending']:
            self.cache.preload([g['description'] for g in goals['pending']])
        
        # 5. Spawn evolver if needed
        if stagnation >= 0.7:
            await self._spawn_evolver()
        
        # 6. Process goals in parallel
        if goals['pending']:
            workers = min(len(goals['pending']), self.max_workers)
            results = await asyncio.gather(*[
                self._spawn_worker(g) 
                for g in goals['pending'][:workers]
            ])
        
        return {
            "interval": self.current_interval,
            "activity": activity,
            "stagnation": stagnation,
            "workers_spawned": len(results) if goals['pending'] else 0
        }
    
    def _assess_activity(self) -> str:
        """
        Assess current activity level.
        
        Factors:
        - Pending goals count
        - Recent observation rate
        - GLM-5 budget remaining
        """
        pending_goals = len(self._get_pending_goals())
        recent_obs = len(self.observer.get_recent_observations(10))
        budget = self.budget.remaining()
        
        if pending_goals >= 5 or recent_obs >= 8:
            return "high"
        elif pending_goals >= 2 or recent_obs >= 4:
            return "medium"
        else:
            return "low"
    
    def _calculate_interval(self, activity: str) -> int:
        """Calculate adaptive interval based on activity."""
        
        intervals = {
            "high": 30,     # 30 seconds
            "medium": 120,  # 2 minutes
            "low": 600      # 10 minutes
        }
        
        target = intervals[activity]
        
        # Smooth transition
        return int(self.current_interval * 0.7 + target * 0.3)
```

**Predictive Cache:**

```python
class PredictiveCache:
    """
    Pre-load context for likely tasks.
    
    Strategies:
    1. Task type → Template + Bloodline
    2. Time of day → Expected categories
    3. Recent patterns → Similar ancestors
    """
    
    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=300)  # 5 min TTL
        self.hit_rate = 0.0
        
    def preload(self, task_descriptions: List[str]):
        """Pre-load context for likely tasks."""
        
        for task in task_descriptions:
            # Classify task type
            task_type = self._classify_task_type(task)
            
            # Pre-load template
            template = self._load_template(task_type)
            
            # Pre-load bloodline
            bloodline = self._load_bloodline(task_type)
            
            # Pre-search ancestors
            ancestors = self._search_ancestors(task)
            
            # Cache all
            self.cache[task] = {
                "template": template,
                "bloodline": bloodline,
                "ancestors": ancestors
            }
    
    def get(self, task: str) -> Optional[Dict]:
        """Get cached context if available."""
        if task in self.cache:
            self.hit_rate = self.hit_rate * 0.9 + 0.1  # Update running average
            return self.cache[task]
        return None
```

**Performance Improvement:**
- Active response: 5min → 30s (10x faster)
- Parallel workers: 1 → 5 (5x throughput)
- Cache hit rate: 0% → 80% (saves ~500ms per hit)

---

### 4. Smart Rate Limiter V2

**V1 Problems:**
- Manual fallback on 429
- No retry with backoff
- Max 2 concurrent requests

**V2 Solutions:**

```python
class SmartRateLimiterV2:
    """
    Intelligent rate limit handling for GLM-4.7-Flash.
    
    Features:
    - Automatic retry with exponential backoff
    - Request queue with priority
    - Circuit breaker pattern
    - Predictive throttling
    """
    
    def __init__(self):
        self.max_concurrent = 2
        self.active_requests = 0
        self.queue = asyncio.PriorityQueue()
        self.backoff_until = 0
        self.consecutive_429s = 0
        self.fallback_model = "phi3:mini"
        
    async def execute(self, request: Request) -> Response:
        """Execute request with smart rate limiting."""
        
        # Check circuit breaker
        if time.time() < self.backoff_until:
            return await self._fallback(request)
        
        # Wait for slot
        while self.active_requests >= self.max_concurrent:
            await asyncio.sleep(0.05)  # 50ms poll
        
        # Execute with retry
        self.active_requests += 1
        try:
            response = await self._execute_with_retry(request)
            self.consecutive_429s = 0
            return response
        finally:
            self.active_requests -= 1
    
    async def _execute_with_retry(self, request: Request, attempts: int = 3) -> Response:
        """Execute with exponential backoff retry."""
        
        for attempt in range(attempts):
            try:
                return await self._call_glm_flash(request)
            except RateLimitError:
                self.consecutive_429s += 1
                
                # Exponential backoff
                wait_time = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s
                
                # Circuit breaker on repeated failures
                if self.consecutive_429s >= 3:
                    self.backoff_until = time.time() + 30  # 30s cooldown
                    return await self._fallback(request)
                
                await asyncio.sleep(wait_time)
        
        # All retries failed - use fallback
        return await self._fallback(request)
    
    async def _fallback(self, request: Request) -> Response:
        """Fallback to local model."""
        return await self._call_phi3_mini(request)
    
    async def _call_glm_flash(self, request: Request) -> Response:
        """Call GLM-4.7-Flash API."""
        # Implementation for zai/glm-4.7-flash
        pass
    
    async def _call_phi3_mini(self, request: Request) -> Response:
        """Call local phi3:mini via Ollama."""
        # Implementation for local fallback
        pass
```

**Request Queue with Priority:**

```python
@dataclass(order=True)
class PrioritizedRequest:
    priority: int  # Lower = higher priority
    request: Request = field(compare=False)
    
    # Priority levels:
    # 0 = Critical (evolver, stagnation response)
    # 1 = High (active goals)
    # 2 = Normal (routine tasks)
    # 3 = Low (background optimization)
```

**Performance Improvement:**
- 429 error rate: ~10% → <1%
- Automatic fallback (no manual intervention)
- Priority queue ensures important requests first

---

### 5. GLM-4.7-Flash Native Integration

**V1 Approach:**
- Used ministral-3 initially
- Switched to GLM-4.7-Flash but kept old patterns

**V2 Optimizations:**

```python
class GLM47FlashOptimized:
    """
    Native GLM-4.7-Flash integration.
    
    Speed: ~3ms per request
    Context: 204K tokens
    Rate limit: Max 2 concurrent
    """
    
    # GLM-4.7-Flash specific optimizations
    OPTIMIZATIONS = {
        # Ultra-short prompts (Flash handles these well)
        "classify": "Task: {task}\nCOMPLEXITY/CATEGORY/CONFIDENCE:",
        
        # Structured output requests
        "fitness": "Task: {task}\nResult: {result}\nSCORE/VERDICT:",
        
        # Pattern extraction
        "patterns": "Result: {result}\nPATTERNS (+trait, -trait):",
        
        # Mutation generation
        "mutate": "Approach: {approach}\n3 MUTATIONS (ADD/MODIFY/REMOVE):",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        })
        
    async def batch_classify(self, tasks: List[str]) -> List[Dict]:
        """
        Batch classification - single request, multiple tasks.
        
        GLM-4.7-Flash can handle batched prompts efficiently.
        """
        prompt = "Classify each task:\n" + "\n".join(
            f"{i}. {t}" for i, t in enumerate(tasks)
        ) + "\n\nFormat: ID/COMPLEXITY/CATEGORY/CONFIDENCE"
        
        response = await self._generate(prompt, max_tokens=200)
        
        # Parse batched response
        results = []
        for line in response.strip().split('\n'):
            parts = line.split('/')
            if len(parts) >= 4:
                results.append({
                    "complexity": parts[1],
                    "category": parts[2],
                    "confidence": parts[3]
                })
        
        return results
```

**Request Batching:**

```python
class BatchProcessor:
    """
    Batch multiple requests into single API call.
    
    GLM-4.7-Flash supports batched prompts efficiently.
    Reduces API calls by 5-10x.
    """
    
    def __init__(self, batch_size: int = 5, max_wait_ms: int = 50):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.pending = []
        
    async def submit(self, request: Request) -> Response:
        """Submit request to batch queue."""
        
        future = asyncio.Future()
        self.pending.append((request, future))
        
        # Process batch if full or after timeout
        if len(self.pending) >= self.batch_size:
            await self._process_batch()
        else:
            asyncio.create_task(self._wait_and_process())
        
        return await future
    
    async def _process_batch(self):
        """Process batched requests in single API call."""
        
        if not self.pending:
            return
        
        batch = self.pending[:self.batch_size]
        self.pending = self.pending[self.batch_size:]
        
        # Combine into single prompt
        combined_prompt = self._combine_prompts([r for r, _ in batch])
        
        # Single API call
        response = await self.glm_flash.generate(combined_prompt)
        
        # Split response and resolve futures
        results = self._split_response(response, len(batch))
        for (_, future), result in zip(batch, results):
            future.set_result(result)
```

**Performance Improvement:**
- API calls: Reduced by 5-10x via batching
- Latency: ~3ms per request (same, but more work per call)
- Better GLM-4.7-Flash utilization

---

## V2 Performance Targets

| Metric | V1 Baseline | V2 Target | Improvement |
|--------|-------------|-----------|-------------|
| Evolution cycle | 15 seconds | 3 seconds | 5x faster |
| Pattern search | 1000ms | 10ms | 100x faster |
| Heartbeat response | 5 minutes | 30 seconds (active) | 10x faster |
| Cache hit rate | 0% | 80% | ∞ |
| 429 error rate | ~10% | <1% | 10x better |
| Parallel workers | 1 | 5 | 5x throughput |
| GLM-5 requests per evolution | 3-5 | 0 (simulation) | 100% savings |

---

## V2 Implementation Priority

### Phase 1: Rate Limit Resilience (Week 1)
- [ ] Smart rate limiter with exponential backoff
- [ ] Automatic fallback to phi3:mini
- [ ] Request queue with priority

### Phase 2: Observer V2 (Week 2)
- [ ] SQLite + ChromaDB storage
- [ ] Vector-indexed pattern search
- [ ] Real-time stagnation detection

### Phase 3: Evolver V2 (Week 3)
- [ ] Parallel mutation generation
- [ ] In-memory simulation
- [ ] Multi-objective fitness
- [ ] Pareto-optimal selection

### Phase 4: Heartbeat V2 (Week 4)
- [ ] Adaptive interval
- [ ] Parallel goal processing
- [ ] Predictive cache

### Phase 5: GLM-4.7-Flash Optimization (Week 5)
- [ ] Request batching
- [ ] Optimized prompts
- [ ] Native integration patterns

---

## V2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SPARK LOOP V2 - FULL FLOW                            │
│                                                                              │
│   USER TASK                                                                  │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ MAIN SESSION (Sloth_rog)                                            │  │
│   │                                                                      │  │
│   │   1. Classify task ──────────────────► GLM-4.7-Flash (~3ms)        │  │
│   │   2. Check cache ◄─────────────────── Predictive Cache (80% hit)   │  │
│   │   3. Spawn Large Meeseeks ───────────► GLM-5 (if complex)          │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ LARGE MEESEEKS (GLM-5) - Director                                   │  │
│   │                                                                      │  │
│   │   - Think using 128K context                                        │  │
│   │   - Command mini workers                                            │  │
│   │   - Report to user                                                  │  │
│   │                                                                      │  │
│   │   Commands:                                                          │  │
│   │   MINI: crypt/search/memory/write/entomb                           │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ MINI POOL (GLM-4.7-Flash) - Workers                                 │  │
│   │                                                                      │  │
│   │   [Worker 1] ──┐                                                    │  │
│   │   [Worker 2] ──┼──► Smart Rate Limiter ──► Request Queue           │  │
│   │   [Fallback] ──┘    (max 2 concurrent)      (priority order)       │  │
│   │                                                                      │  │
│   │   Tasks:                                                             │  │
│   │   - Search crypt (vector search, 10ms)                              │  │
│   │   - Load context (cached, 1ms)                                      │  │
│   │   - Write files (100ms)                                             │  │
│   │   - Entomb results (30ms)                                           │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ OBSERVER V2 (Vector-Indexed)                                        │  │
│   │                                                                      │  │
│   │   - Record observation → SQLite + ChromaDB                          │  │
│   │   - Detect patterns → Semantic clustering                           │  │
│   │   - Stagnation → Real-time streaming analysis                       │  │
│   │                                                                      │  │
│   │   If stagnation >= 70%:                                             │  │
│   │       → Spawn Evolver V2                                            │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                      │
│       ▼ (if stagnation)                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ EVOLVER V2 (Parallel)                                               │  │
│   │                                                                      │  │
│   │   1. Generate 5 mutations ──► Parallel (GLM-4.7-Flash x5, ~15ms)   │  │
│   │   2. Simulate all ─────────► In-memory (no GLM-5 cost)             │  │
│   │   3. Multi-obj fitness ────► Pareto selection                       │  │
│   │   4. Apply best ───────────► Template update                        │  │
│   │                                                                      │  │
│   │   Total: ~3 seconds (5x faster than V1)                             │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ HEARTBEAT V2 (Adaptive)                                             │  │
│   │                                                                      │  │
│   │   - Assess activity ──► Adjust interval (30s - 10min)               │  │
│   │   - Check goals ──────► Process in parallel (up to 5)               │  │
│   │   - Pre-cache ────────► Predictive context loading                  │  │
│   │   - Budget aware ─────► Schedule based on GLM-5 remaining           │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                      │
│       └──────────────────────► LOOP CONTINUES AUTONOMOUSLY                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## V2 Fitness Function - Multi-Objective

**V1 Fitness (Simple Linear):**
```python
fitness = (success_rate * 0.7) +
          (speed_bonus * 0.1) +
          (efficiency_bonus * 0.1) +
          (perfect_success_bonus * 0.1)
```

**V2 Fitness (Multi-Objective Pareto):**

```python
def multi_objective_fitness(mutation: Mutation, simulation: Simulation) -> Dict[str, float]:
    """
    Multi-objective fitness for Pareto optimization.
    
    No single score - instead, find Pareto front of non-dominated solutions.
    """
    return {
        # Primary objectives (maximize)
        "success_rate": simulation.predicted_success_rate,
        "speed": 1.0 / simulation.predicted_duration,
        "token_efficiency": simulation.predicted_token_efficiency,
        
        # Secondary objectives
        "novelty": calculate_novelty(mutation),  # Encourage diversity
        "stability": 1.0 / simulation.predicted_variance,  # Reliable results
        
        # Context-specific weights
        "task_fit": calculate_task_fit(mutation, current_task_type),
        
        # Risk assessment
        "risk_score": calculate_risk(mutation),  # Minimize
    }

def pareto_select(mutations: List[Mutation], fitness: List[Dict]) -> List[Mutation]:
    """
    Select Pareto-optimal mutations.
    
    A mutation is Pareto-optimal if no other mutation is better in all objectives.
    """
    pareto_front = []
    
    for i, m in enumerate(mutations):
        is_dominated = False
        
        for j, other in enumerate(mutations):
            if i == j:
                continue
            
            # Check if j dominates i
            if dominates(fitness[j], fitness[i]):
                is_dominated = True
                break
        
        if not is_dominated:
            pareto_front.append(m)
    
    return pareto_front

def dominates(a: Dict, b: Dict) -> bool:
    """Check if fitness a dominates fitness b."""
    better_in_any = False
    
    for key in a:
        if key == "risk_score":  # Minimize
            if a[key] > b[key]:
                return False
            if a[key] < b[key]:
                better_in_any = True
        else:  # Maximize
            if a[key] < b[key]:
                return False
            if a[key] > b[key]:
                better_in_any = True
    
    return better_in_any
```

---

## V2 Bottleneck Analysis

### Remaining Bottlenecks After V2

| Bottleneck | V2 Status | Future Solution |
|------------|-----------|-----------------|
| GLM-5 budget (400/5hrs) | Unchanged | Multi-model fallback |
| Crypt search speed | Solved (vector index) | - |
| Rate limits | Mitigated (smart queue) | Distributed API keys |
| Single main session | Unchanged | Multi-agent coordination |
| Template mutation quality | Improved (simulation) | Reinforcement learning |

---

## V2 Model Stack

| Role | Model | Speed | Cost | Use Case |
|------|-------|-------|------|----------|
| **Main Agent** | GLM-4.7 | Fast | Paid | Coordination |
| **Large Meeseeks** | GLM-5 | Medium | 400/5hrs | Complex reasoning |
| **Mini Meeseeks** | GLM-4.7-Flash | **~3ms** | FREE | Fast tasks |
| **Fallback** | phi3:mini | 200-800ms | FREE | Rate limit fallback |
| **Embeddings** | nomic-embed-text | 45ms | FREE | Vector search |
| **Vector DB** | ChromaDB | <10ms | FREE | Pattern storage |

---

## V2 File Structure

```
the-crypt/spark-loop-v2/
├── observer_v2.py              # Vector-indexed observer
├── evolver_v2.py               # Parallel evolver
├── heartbeat_v2.py             # Adaptive heartbeat
├── rate_limiter_v2.py          # Smart rate limiter
├── batch_processor.py          # Request batching
├── predictive_cache.py         # Context pre-loading
├── mutation_simulator.py       # In-memory simulation
├── fitness_v2.py               # Multi-objective fitness
├── observer_vectors/           # ChromaDB storage
├── observer_v2.db              # SQLite database
└── SPARK-LOOP-V2.md            # This document
```

---

## V2 Success Metrics

### Week 1 Targets
- [ ] 429 error rate < 1%
- [ ] Automatic fallback working
- [ ] Priority queue operational

### Week 2 Targets
- [ ] Pattern search < 10ms
- [ ] Real-time stagnation detection
- [ ] Vector index built

### Week 3 Targets
- [ ] Evolution cycle < 5 seconds
- [ ] Simulation-based testing
- [ ] Pareto selection working

### Week 4 Targets
- [ ] Adaptive heartbeat interval
- [ ] 5 parallel workers
- [ ] 80% cache hit rate

### Week 5 Targets
- [ ] Request batching operational
- [ ] GLM-4.7-Flash fully optimized
- [ ] Full V2 integration

---

## Conclusion

**V2 Evolution Summary:**

1. **Speed**: 5x faster evolution cycles (15s → 3s)
2. **Resilience**: Zero 429 failures with smart rate limiting
3. **Efficiency**: 80% cache hit rate, no GLM-5 for testing
4. **Scale**: 100x faster pattern search, 5x worker throughput
5. **Intelligence**: Multi-objective optimization, predictive caching

**The Spark Loop V2 is designed for autonomous, self-improving AGI evolution at unprecedented speed.**

---

🔥⚡ **V2: EVOLVED FOR SPEED. BUILT FOR AGI.**

*Created: 2026-03-01*
*Author: Spark Loop Evolution Subagent*
*Status: V2 SPECIFICATION COMPLETE*
