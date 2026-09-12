import '../models/candidate.dart';

const List<Candidate> dummyCandidates = [
  Candidate(
    id: 'CAN-0001',
    candidateNumber: 1,
    name: 'Elena Rostova',
    headline: 'Principal Distributed Systems Architect',
    location: 'Zurich, Switzerland',
    email: 'elena.rostova@nexus-systems.io',
    phone: '+41 44 215 8890',
    portfolioUrl: 'https://rostova.systems',
    githubUrl: 'https://github.com/erostova-sys',
    matchScore: 97,
    yearsOfExperience: 11,
    category: 'Systems & Distributed',
    previewSnippet:
        'Architected fault-tolerant distributed consensus engines handling 4.2M events/sec. Former L7 Infrastructure Lead at CloudScale.',
    summary:
        'Principal Systems Architect specializing in zero-downtime consensus protocols, low-latency asynchronous networking, and multi-region distributed databases. Over 11 years designing enterprise-scale infrastructure, Raft/Paxos consensus clusters, and self-healing runtime systems with sub-5ms P99 latency guarantees.',
    skills: [
      'Rust',
      'Go',
      'Raft / Paxos',
      'Distributed DBs',
      'gRPC / Protobuf',
      'Kubernetes',
      'eBPF',
      'Linux Kernel Internals',
      'Actor Systems',
      'Kafka / Flink',
    ],
    experiences: [
      WorkExperience(
        role: 'Principal Systems Architect',
        company: 'Vortex Storage & Compute',
        location: 'Zurich & Remote',
        period: '2021 — PRESENT',
        bullets: [
          'Engineered custom Raft-based consensus fabric serving 4.2M transactional writes per second with sub-4ms P99 commit latencies.',
          'Reduced global cross-datacenter synchronization bandwidth by 38% utilizing differential delta compression and pipelined streaming replication.',
          'Led architecture review board across 6 distributed infrastructure squads overseeing core storage engine reliability.',
        ],
      ),
      WorkExperience(
        role: 'Staff Infrastructure Engineer',
        company: 'CloudScale Global Inc.',
        location: 'Berlin, Germany',
        period: '2017 — 2021',
        bullets: [
          'Designed high-throughput L7 proxy tier processing over 120 billion weekly requests across 28 multi-cloud geographical regions.',
          'Pioneered eBPF-driven zero-copy network telemetry that reduced CPU overhead by 26% across 14,000 container workloads.',
          'Mentored 12 senior and staff engineers across core runtime, networking, and observability teams.',
        ],
      ),
      WorkExperience(
        role: 'Senior C++ / Systems Developer',
        company: 'Aether MicroKernels',
        location: 'Munich, Germany',
        period: '2013 — 2017',
        bullets: [
          'Contributed to async I/O subsystems and lock-free ring buffer implementations in C++14/17.',
          'Automated fuzz testing pipeline finding 34 race conditions before production kernel deployment.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Distributed Computing & Computer Systems',
        institution: 'ETH Zürich',
        year: '2013',
        details: 'Graduated with Highest Honors · Thesis: Deterministic Replay in Asynchronous Actor Networks',
      ),
      Education(
        degree: 'B.S. in Computer Science & Applied Mathematics',
        institution: 'Technical University of Munich',
        year: '2011',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'ChronoConsensus',
        description: 'Open-source distributed state machine in Rust with built-in Byzantine fault tolerance and pluggable storage backends.',
        techStack: ['Rust', 'Tokio', 'RocksDB', 'QuickCheck'],
        link: 'https://github.com/erostova/chronoconsensus',
      ),
      ResumeProject(
        name: 'NetTrace-eBPF',
        description: 'Microsecond TCP window analysis tool hooked via kernel eBPF probes for detecting silent link packet degradation.',
        techStack: ['C', 'eBPF', 'Go', 'BCC'],
        link: 'https://github.com/erostova/nettrace-ebpf',
      ),
    ],
    certifications: [
      'Certified Kubernetes Security Specialist (CKS)',
      'Linux Foundation Systems Programming Fellow',
    ],
  ),
  Candidate(
    id: 'CAN-0002',
    candidateNumber: 2,
    name: 'Marcus Vance',
    headline: 'Senior Generative AI & LLM Systems Engineer',
    location: 'San Francisco, CA',
    email: 'marcus.vance@synthetic-logic.dev',
    phone: '+1 415 555 0192',
    portfolioUrl: 'https://marcusvance.ai',
    githubUrl: 'https://github.com/mvance-ai',
    matchScore: 96,
    yearsOfExperience: 8,
    category: 'AI & Machine Learning',
    previewSnippet:
        'Specialist in high-throughput LLM serving, speculative decoding, and quantized model compilation. Ex-Anthropic contractor.',
    summary:
        'Machine learning systems engineer bridging model architectures and production deployment. Deep expertise in high-throughput inference optimization (vLLM, TensorRT-LLM, speculative decoding), distributed training orchestration, and custom continuous batching runtimes on H100/A100 clusters.',
    skills: [
      'Python',
      'PyTorch',
      'CUDA / Triton',
      'TensorRT-LLM',
      'vLLM',
      'Speculative Decoding',
      'FlashAttention',
      'Distributed Training',
      'Hugging Face',
      'Ray Train/Serve',
    ],
    experiences: [
      WorkExperience(
        role: 'Lead AI Infrastructure Engineer',
        company: 'Cognitive Foundry',
        location: 'San Francisco, CA',
        period: '2022 — PRESENT',
        bullets: [
          'Architected an inference serving fleet hosting 70B+ parameter models achieving 3.4x higher token throughput via custom speculative decoding.',
          'Engineered Triton CUDA kernels for mixed-precision FP8 attention that cut memory bandwidth bottlenecks by 31%.',
          'Managed 512x H100 cluster utilizing SLURM, Ray, and Megatron-LM for continuous domain-specific model fine-tuning.',
        ],
      ),
      WorkExperience(
        role: 'Senior Machine Learning Engineer',
        company: 'Synthetix Research',
        location: 'Palo Alto, CA',
        period: '2019 — 2022',
        bullets: [
          'Built production semantic search and retrieval augmented generation (RAG) pipelines querying 500M+ vector embeddings in <18ms.',
          'Authored quant-aware pruning techniques reducing model weights by 60% with less than 0.8% loss in MMLU benchmarks.',
        ],
      ),
      WorkExperience(
        role: 'ML Research Engineer',
        company: 'Berkeley AI Lab',
        location: 'Berkeley, CA',
        period: '2016 — 2019',
        bullets: [
          'Researched multi-modal representation alignment and transformer distillation architectures under NSF grant sponsorship.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Artificial Intelligence & Robotics',
        institution: 'Stanford University',
        year: '2016',
      ),
      Education(
        degree: 'B.S. in Electrical Engineering & Computer Science',
        institution: 'UC Berkeley',
        year: '2014',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'FlashBatch-LLM',
        description: 'Lightweight asynchronous continuous batching engine built on top of C++ and PyTorch C++ API for sub-millisecond dispatching.',
        techStack: ['C++', 'CUDA', 'Python', 'PyTorch'],
        link: 'https://github.com/mvance/flashbatch-llm',
      ),
      ResumeProject(
        name: 'SparseKV-Compress',
        description: 'Context compression algorithm for 128k context windows preserving retrieval needle-in-haystack fidelity with 4x KV cache reduction.',
        techStack: ['Python', 'Triton', 'JAX'],
      ),
    ],
    certifications: [
      'NVIDIA Certified Deep Learning Institute Ambassador',
      'AWS Certified Machine Learning Specialty',
    ],
  ),
  Candidate(
    id: 'CAN-0003',
    candidateNumber: 3,
    name: 'Julian De Vries',
    headline: 'Creative Technologist & WebGL / Flutter Lead',
    location: 'Amsterdam, Netherlands',
    email: 'julian@studio-devries.nl',
    phone: '+31 20 892 4110',
    portfolioUrl: 'https://juliandevries.design',
    githubUrl: 'https://github.com/juliandevries',
    matchScore: 94,
    yearsOfExperience: 9,
    category: 'Creative & Frontend',
    previewSnippet:
        'Award-winning creative developer. Awwwards Site of the Year nominee. Blends procedural shaders, Flutter Web canvaskit, and micro-interactions.',
    summary:
        'Creative developer and design engineer crafting tactile, fluid digital artifacts. Pioneer in bridging high-performance WebGL/WebGPU graphics shaders with reactive Flutter Web applications and bespoke design systems. Obsessive attention to typography, kinetic easing curves, and organic interactive physics.',
    skills: [
      'Flutter / Dart',
      'Three.js / WebGL',
      'WebGPU',
      'GLSL Shaders',
      'TypeScript',
      'Design Systems',
      'CanvasKit',
      'Micro-interactions',
      'SVG Math & Geometry',
      'Figma Tokens',
    ],
    experiences: [
      WorkExperience(
        role: 'Head of Creative Technology',
        company: 'Atelier Monochrome',
        location: 'Amsterdam & Paris',
        period: '2020 — PRESENT',
        bullets: [
          'Led interactive design engineering for luxury fashion houses and digital galleries, winning 3x Awwwards Site of the Day.',
          'Built high-performance custom Flutter Web renderer module integrating GLSL fragment shaders directly into Flutter CanvasKit pipeline.',
          'Architected design token compiler unifying Figma variable tokens with Dart theme definitions for 100% pixel-perfect fidelity.',
        ],
      ),
      WorkExperience(
        role: 'Senior Interactive Engineer',
        company: 'Kinetic Works',
        location: 'Rotterdam, Netherlands',
        period: '2017 — 2020',
        bullets: [
          'Developed 60fps 3D product visualizer in Three.js and Flutter Web, boosting consumer time-on-page by 210%.',
          'Wrote bespoke particle simulation engine simulating dynamic fluid physics on mobile web browsers.',
        ],
      ),
      WorkExperience(
        role: 'Frontend UI/UX Developer',
        company: 'Studiovision Labs',
        location: 'Utrecht, Netherlands',
        period: '2015 — 2017',
        bullets: [
          'Constructed accessible, fluid component libraries used across 40+ client production applications.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'B.A. in Interaction Design & Digital Media Arts',
        institution: 'Design Academy Eindhoven',
        year: '2015',
        details: 'Graduated Cum Laude · Thesis: Spatial Choreography in Screen Typography',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'ShaderCanvas-Flutter',
        description: 'Declarative Flutter package for compiling runtime GLSL fragment shaders with automatic hot-reload previewing on Flutter Web.',
        techStack: ['Flutter', 'Dart', 'GLSL', 'CanvasKit'],
        link: 'https://github.com/jdevries/shader-canvas',
      ),
      ResumeProject(
        name: 'Tactile-Scroll',
        description: 'Inertial momentum scrolling engine with spring dampening and haptic feedback simulation for desktop browser viewports.',
        techStack: ['TypeScript', 'WebGL', 'WebAudio'],
      ),
    ],
    certifications: [
      'Figma Certified Design System Architect',
      'W3C Web Accessibility Specialist',
    ],
  ),
  Candidate(
    id: 'CAN-0004',
    candidateNumber: 4,
    name: 'Dr. Sarah Chen',
    headline: 'Staff AI/ML Research Scientist',
    location: 'Boston, MA',
    email: 'sarah.chen@mit-alum.edu',
    phone: '+1 617 555 4921',
    portfolioUrl: 'https://sarahchen-ai.org',
    githubUrl: 'https://github.com/schen-research',
    matchScore: 93,
    yearsOfExperience: 10,
    category: 'AI & Machine Learning',
    previewSnippet:
        'Ph.D. in Computer Science from MIT. 14 publications across NeurIPS/ICML. Specializes in graph neural networks and causal inference.',
    summary:
        'Research scientist and technical leader focusing on robust graph representation learning, self-supervised pre-training, and mechanistic interpretability. Combines theoretical machine learning grounding with pragmatic algorithmic efficiency for large-scale enterprise deployments.',
    skills: [
      'PyTorch',
      'Graph Neural Nets',
      'Self-Supervised Learning',
      'Mechanistic Interpretability',
      'NumPy / SciPy',
      'Distributed Training',
      'Python / C++',
      'JAX / Flax',
      'Causal Inference',
      'MLOps',
    ],
    experiences: [
      WorkExperience(
        role: 'Staff Research Scientist',
        company: 'Helix Cognitive Labs',
        location: 'Boston, MA',
        period: '2021 — PRESENT',
        bullets: [
          'Led 8-person research pod creating multi-relational graph transformer networks for molecular property prediction.',
          'Filed 4 core algorithmic patents in equivariant neural representations, reducing training sample complexity by 55%.',
          'Collaborated with production engineering teams to distill research prototypes into scalable sub-50ms inference APIs.',
        ],
      ),
      WorkExperience(
        role: 'Senior Machine Learning Researcher',
        company: 'DeepHorizon Institute',
        location: 'Cambridge, MA',
        period: '2017 — 2021',
        bullets: [
          'Authored 9 papers accepted at NeurIPS, ICML, and ICLR on causal feature discovery and attention head attribution.',
          'Built internal interpretability toolkit visualizing activation vectors across deep transformer layers.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'Ph.D. in Computer Science (Artificial Intelligence)',
        institution: 'Massachusetts Institute of Technology (MIT)',
        year: '2017',
        details: 'Adviser: Prof. Leslie Kaelbling · NSF Graduate Research Fellow',
      ),
      Education(
        degree: 'B.S. in Mathematics and Computer Science',
        institution: 'Carnegie Mellon University',
        year: '2012',
        details: 'Phi Beta Kappa · University Honors',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'GraphX-Attn',
        description: 'Scalable graph attention operator achieving linear memory complexity with respect to edge degree.',
        techStack: ['PyTorch', 'CUDA', 'Python'],
        link: 'https://github.com/schen/graphx-attn',
      ),
      ResumeProject(
        name: 'AttnProbe',
        description: 'Open-source mechanistic interpretability suite inspecting residual streams and induction heads in foundation models.',
        techStack: ['JAX', 'Python', 'Streamlit'],
      ),
    ],
    certifications: [
      'IEEE Senior Member',
      'NeurIPS Outstanding Reviewer Award (2022, 2024)',
    ],
  ),
  Candidate(
    id: 'CAN-0005',
    candidateNumber: 5,
    name: 'Liam O\'Connor',
    headline: 'Principal Site Reliability & Cloud Architect',
    location: 'Dublin, Ireland',
    email: 'liam.oconnor@sre-arch.net',
    phone: '+353 1 496 0184',
    portfolioUrl: 'https://oconnor-infra.com',
    githubUrl: 'https://github.com/liam-sre',
    matchScore: 92,
    yearsOfExperience: 12,
    category: 'Cloud & Infrastructure',
    previewSnippet:
        'Mastery of multi-cloud disaster recovery, Kubernetes multi-cluster federation, and automated chaos engineering at petabyte scale.',
    summary:
        'Site reliability engineering director and cloud architect with 12+ years championing 99.999% availability SLAs for Tier-1 financial and SaaS platforms. Specialist in immutable infrastructure, automated incident self-healing, multi-region Kubernetes mesh, and finOps cloud cost optimization.',
    skills: [
      'Kubernetes (K8s)',
      'Terraform / OpenTofu',
      'AWS / GCP / Azure',
      'Istio / Envoy',
      'Prometheus / Grafana',
      'Chaos Engineering',
      'FinOps & Cost Mgmt',
      'Go / Bash / Python',
      'ArgoCD / GitOps',
      'Incident Commander',
    ],
    experiences: [
      WorkExperience(
        role: 'Principal SRE Architect',
        company: 'Starlight Financial Systems',
        location: 'Dublin & London',
        period: '2020 — PRESENT',
        bullets: [
          'Governed infrastructure posture for core payment gateways processing €42B annually with zero unbudgeted downtime.',
          'Constructed automated chaos engineering platform executing synthetic region blackout failovers every fortnight.',
          'Cut multi-cloud compute and network spend by \$2.4M annually via rightsizing and spot-orchestration policies.',
        ],
      ),
      WorkExperience(
        role: 'Lead Cloud Infrastructure Engineer',
        company: 'Nordic Cloud Alliance',
        location: 'Dublin, Ireland',
        period: '2016 — 2020',
        bullets: [
          'Migrated legacy monolithic colocation architecture to 18-cluster federated Kubernetes topology across AWS and GCP.',
          'Authored Terraform modules governing 4,500+ cloud resources with strict automated Open Policy Agent (OPA) checks.',
        ],
      ),
      WorkExperience(
        role: 'Systems Administrator / DevOps Engineer',
        company: 'Celtic Telecom Networks',
        location: 'Galway, Ireland',
        period: '2012 — 2016',
        bullets: [
          'Managed carrier-grade Linux servers, DNS backbones, and optical routing switching gear.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'B.Sc. in Computer Networks & Distributed Systems',
        institution: 'Trinity College Dublin',
        year: '2012',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'AutoRemediate-Operator',
        description: 'Kubernetes custom controller automatically triggering memory dump captures and proactive pod restarts before OOMKilled events occur.',
        techStack: ['Go', 'Kubernetes client-go', 'Prometheus API'],
      ),
    ],
    certifications: [
      'Certified Kubernetes Administrator (CKA)',
      'AWS Solutions Architect Professional',
      'Google Cloud Certified Fellow — Cloud Infrastructure',
    ],
  ),
  Candidate(
    id: 'CAN-0006',
    candidateNumber: 6,
    name: 'Amara Diallo',
    headline: 'Senior Full-Stack Distributed Engineer',
    location: 'London, UK',
    email: 'amara.diallo@stack-craft.co.uk',
    phone: '+44 20 7946 0912',
    portfolioUrl: 'https://amaradiallo.dev',
    githubUrl: 'https://github.com/adiallo-dev',
    matchScore: 91,
    yearsOfExperience: 7,
    category: 'Full-Stack & Web',
    previewSnippet:
        'Architect of high-concurrency collaborative apps. Expert in CRDTs, WebSocket multiplexing, and resilient TypeScript/Go microservices.',
    summary:
        'Full-stack engineer passionate about collaborative real-time web applications. Deep experience in conflict-free replicated data types (CRDTs), state synchronization over WebSockets, and architecting resilient backend services in Go and Node.js serving millions of active users.',
    skills: [
      'TypeScript / Node.js',
      'Go',
      'CRDTs (Yjs, Automerge)',
      'WebSockets / WebRTC',
      'React / Next.js',
      'PostgreSQL / Redis',
      'GraphQL / REST',
      'Docker',
      'TailwindCSS',
      'Distributed State',
    ],
    experiences: [
      WorkExperience(
        role: 'Staff Full-Stack Engineer',
        company: 'CanvasFlow Interactive',
        location: 'London, UK',
        period: '2022 — PRESENT',
        bullets: [
          'Architected the real-time collaborative sync engine powering 300,000 concurrent active document editors using Yjs and WebRTC mesh.',
          'Engineered low-latency Go microservice gateway handling 1.8M sustained WebSocket connections with heartbeat throttling.',
          'Reduced time-to-interactive (TTI) on web clients by 44% through selective hydration and route chunk streaming.',
        ],
      ),
      WorkExperience(
        role: 'Senior Full-Stack Developer',
        company: 'Verve Technologies',
        location: 'London, UK',
        period: '2019 — 2022',
        bullets: [
          'Built internal design system and high-throughput inventory management dashboards serving enterprise logistics clients.',
          'Migrated legacy REST APIs to schema-federated GraphQL, improving mobile client battery consumption by 18%.',
        ],
      ),
      WorkExperience(
        role: 'Software Engineer',
        company: 'Novus Digital',
        location: 'Bristol, UK',
        period: '2017 — 2019',
        bullets: [
          'Developed responsive progressive web applications (PWAs) with offline-first indexedDB storage caching.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'B.Eng. in Software Engineering',
        institution: 'Imperial College London',
        year: '2017',
        details: 'First Class Honours',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'SyncState-CRDT',
        description: 'Minimalist hybrid JSON CRDT with pluggable persistent storage and peer-to-peer WebRTC gossip synchronization.',
        techStack: ['TypeScript', 'WebRTC', 'IndexedDB'],
      ),
    ],
    certifications: [
      'HashiCorp Certified Terraform Associate',
      'MongoDB Certified Developer Associate',
    ],
  ),
  Candidate(
    id: 'CAN-0007',
    candidateNumber: 7,
    name: 'Kenji Takahashi',
    headline: 'High-Frequency Systems & Rust Kernel Engineer',
    location: 'Tokyo, Japan',
    email: 'kenji.takahashi@tokyo-systems.jp',
    phone: '+81 3 5555 0834',
    portfolioUrl: 'https://takahashi.dev.jp',
    githubUrl: 'https://github.com/ktakahashi-kernel',
    matchScore: 90,
    yearsOfExperience: 9,
    category: 'Systems & Distributed',
    previewSnippet:
        'Zero-allocation Rust specialist. Focus on lock-free data structures, memory-mapped ring buffers, and sub-microsecond tick-to-trade engines.',
    summary:
        'Systems engineer focused on bare-metal execution, hardware cache optimization, and microsecond order execution pipelines. Expert in Rust, modern C++ (C++20), lockless algorithmic queues, PCIe memory-mapped ring buffers, and kernel bypass networking (DPDK).',
    skills: [
      'Rust (Bare-metal & Async)',
      'Modern C++ (C++20/23)',
      'DPDK Kernel Bypass',
      'Lock-Free Concurrency',
      'SIMD / AVX-512',
      'Linux Perf / Valgrind',
      'Cache Coherency',
      'Assembly (x86_64)',
      'FPGA Interfacing',
      'Low Latency OS Tuning',
    ],
    experiences: [
      WorkExperience(
        role: 'Lead Low-Latency Systems Engineer',
        company: 'Sakura Quantitative Partners',
        location: 'Tokyo, Japan',
        period: '2021 — PRESENT',
        bullets: [
          'Engineered market connectivity gateway achieving tick-to-quote latency under 850 nanoseconds on solarflare network cards.',
          'Replaced critical C++ order matching paths with memory-safe zero-overhead Rust components with zero runtime panic allocations.',
          'Tuned CPU isolcpus, NUMA node pin affinities, and kernel bypass rings to eliminate OS jitter spikes.',
        ],
      ),
      WorkExperience(
        role: 'Senior Embedded / Systems Developer',
        company: 'Nippon MicroDevices',
        location: 'Kyoto, Japan',
        period: '2016 — 2021',
        bullets: [
          'Authored high-bandwidth DMA drivers and firmware modules for industrial PCIe FPGA accelerator cards.',
          'Optimized vectorized matrix transforms using AVX-512 intrinsics yielding 4.2x speedup.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Information Science and Technology',
        institution: 'University of Tokyo',
        year: '2016',
      ),
      Education(
        degree: 'B.S. in Computer Engineering',
        institution: 'Tokyo Institute of Technology',
        year: '2014',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'Nanofast-Queue',
        description: 'Single-producer single-consumer lock-free ring buffer achieving 45 million operations/sec with zero heap allocations.',
        techStack: ['Rust', 'x86_64 ASM', 'Criterion benchmarks'],
      ),
    ],
    certifications: [
      'Japan Information-Technology Engineers Examination (IPA) — Embedded Systems Specialist',
    ],
  ),
  Candidate(
    id: 'CAN-0008',
    candidateNumber: 8,
    name: 'Maya Lin',
    headline: 'Principal Product & Design Technologist',
    location: 'Seattle, WA',
    email: 'maya.lin@design-arch.co',
    phone: '+1 206 555 7719',
    portfolioUrl: 'https://mayalin.design',
    githubUrl: 'https://github.com/mayalin-ui',
    matchScore: 89,
    yearsOfExperience: 10,
    category: 'Creative & Frontend',
    previewSnippet:
        'Bridging design systems, human-computer interaction, and high-fidelity Flutter/React frontend code. Ex-Airbnb Design Technologist.',
    summary:
        'Hybrid design technologist with a decade of experience designing and writing production frontends for complex software products. Specializes in design token automation, WCAG AAA accessibility, micro-animations, and building multi-platform component architectures in Flutter and React.',
    skills: [
      'Design Engineering',
      'Flutter Web & Mobile',
      'Design Systems Architecture',
      'TypeScript / React',
      'Figma REST API & Tokens',
      'Accessibility (a11y / WCAG)',
      'Motion Design & Choreography',
      'CSS Houdini / Shaders',
      'User Research & Prototyping',
      'Storybook / Widgetbook',
    ],
    experiences: [
      WorkExperience(
        role: 'Principal Design Technologist',
        company: 'Vanguard Systems UX',
        location: 'Seattle, WA',
        period: '2021 — PRESENT',
        bullets: [
          'Architected unified multi-platform design system utilized by 140+ engineers across web, iOS, and Android products.',
          'Developed automated visual regression testing engine catching token deviations across 1,200 UI components before release.',
          'Mentored product designers in writing functional Dart and TypeScript prototypes to accelerate engineering handoffs.',
        ],
      ),
      WorkExperience(
        role: 'Senior Design Systems Engineer',
        company: 'Northstar Media',
        location: 'San Francisco, CA',
        period: '2017 — 2021',
        bullets: [
          'Created accessible data visualization library conforming strictly to WCAG 2.1 AAA color contrast and screen reader standards.',
          'Reduced frontend bundle size by 35% by pruning redundant component dependencies and introducing treeshaking tokens.',
        ],
      ),
      WorkExperience(
        role: 'UX Prototyper',
        company: 'Apex Interactive',
        location: 'Portland, OR',
        period: '2014 — 2017',
        bullets: [
          'Constructed high-fidelity touch-screen prototypes for automotive in-vehicle infotainment consoles.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.Des. in Human-Computer Interaction',
        institution: 'University of Washington',
        year: '2014',
      ),
      Education(
        degree: 'B.S. in Computer Science',
        institution: 'Brown University',
        year: '2012',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'Chroma-Tokens',
        description: 'CLI tool translating W3C Design Token specifications into immutable Dart, CSS variables, and Swift structs with zero manual overhead.',
        techStack: ['TypeScript', 'Dart', 'Node.js', 'Figma API'],
      ),
    ],
    certifications: [
      'Certified Professional in Accessibility Core Competencies (CPACC)',
      'Nielsen Norman UX Master Certified',
    ],
  ),
  Candidate(
    id: 'CAN-0009',
    candidateNumber: 9,
    name: 'David Thorne',
    headline: 'Staff Security & Cryptography Engineer',
    location: 'Austin, TX',
    email: 'david.thorne@cipher-shield.io',
    phone: '+1 512 555 9301',
    portfolioUrl: 'https://thorne-security.org',
    githubUrl: 'https://github.com/dthorne-crypto',
    matchScore: 88,
    yearsOfExperience: 11,
    category: 'Security & Cloud',
    previewSnippet:
        'Zero-knowledge proofs, post-quantum cryptographic primitives, and enterprise threat modeling. Former Red Team lead.',
    summary:
        'Security engineer and applied cryptographer specializing in identity protocols, hardware security modules (HSM), post-quantum algorithms (Kyber, Dilithium), and confidential cloud enclave architectures (AWS Nitro, Intel SGX). Extensive background in offensive red-teaming and secure software supply chains.',
    skills: [
      'Applied Cryptography',
      'Zero-Knowledge Proofs',
      'Rust / Go',
      'Confidential Computing (Nitro)',
      'PKI & Hardware Tokens (HSM)',
      'AppSec & Red Teaming',
      'Threat Modeling (STRIDE)',
      'OAuth2 / OIDC / WebAuthn',
      'Fuzzing & Memory Safety',
      'SOC2 / ISO 27001',
    ],
    experiences: [
      WorkExperience(
        role: 'Staff Security Engineer',
        company: 'Enclave Security Group',
        location: 'Austin, TX',
        period: '2020 — PRESENT',
        bullets: [
          'Engineered key management infrastructure protecting \$12B in digital enterprise assets using multiparty computation (MPC).',
          'Spearheaded zero-trust identity architecture eliminating static developer credentials and enforcing ephemeral WebAuthn certificates.',
          'Discovered 7 high-severity zero-day memory corruption vulnerabilities across internal proprietary network appliances.',
        ],
      ),
      WorkExperience(
        role: 'Senior Cryptographic Engineer',
        company: 'Sentinel Protocols',
        location: 'Washington, DC',
        period: '2016 — 2020',
        bullets: [
          'Implemented post-quantum candidate algorithms for encrypted satellite telemetry links in accordance with NIST guidance.',
          'Constructed automated static analysis rules checking codebases for cryptographic nonce reuse and side-channel timing leaks.',
        ],
      ),
      WorkExperience(
        role: 'Information Security Analyst',
        company: 'Defense Cyber Labs',
        location: 'Arlington, VA',
        period: '2013 — 2016',
        bullets: [
          'Conducted comprehensive penetration testing, vulnerability assessments, and reverse engineering of suspect binaries.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Information Security',
        institution: 'Carnegie Mellon University (CyLab)',
        year: '2013',
      ),
      Education(
        degree: 'B.S. in Computer Science',
        institution: 'University of Texas at Austin',
        year: '2011',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'KyberRust',
        description: 'Constant-time pure Rust implementation of ML-KEM (Kyber) lattice-based post-quantum key encapsulation mechanism.',
        techStack: ['Rust', 'ASM', 'Constant-Time Verification'],
      ),
    ],
    certifications: [
      'Offensive Security Certified Professional (OSCP)',
      'Certified Information Systems Security Professional (CISSP)',
    ],
  ),
  Candidate(
    id: 'CAN-0010',
    candidateNumber: 10,
    name: 'Sofia Rossi',
    headline: 'Senior Computer Vision & Spatial Computing Engineer',
    location: 'Milan, Italy',
    email: 'sofia.rossi@spatial-vision.it',
    phone: '+39 02 7200 4819',
    portfolioUrl: 'https://sofiarossi.vision',
    githubUrl: 'https://github.com/srossi-cv',
    matchScore: 88,
    yearsOfExperience: 8,
    category: 'AI & Machine Learning',
    previewSnippet:
        '3D reconstruction, neural radiance fields (NeRFs), 6DoF tracking, and edge computer vision running on Apple Vision Pro & Meta Quest.',
    summary:
        'Computer vision engineer specializing in 3D scene understanding, Gaussian Splatting, SLAM, and real-time spatial computing. Experienced in taking cutting-edge research algorithms and optimizing them for constrained edge devices and embedded XR headsets at 90fps.',
    skills: [
      'Computer Vision',
      '3D Gaussian Splatting',
      'NeRFs & Photogrammetry',
      'OpenCV / Open3D',
      'CUDA / C++',
      'PyTorch / JAX',
      'SLAM & Visual Odometry',
      'Metal / ARKit / OpenXR',
      'Python',
      'Edge Optimization',
    ],
    experiences: [
      WorkExperience(
        role: 'Lead Spatial Computing Engineer',
        company: 'OmniSpatial Labs',
        location: 'Milan & London',
        period: '2021 — PRESENT',
        bullets: [
          'Engineered real-time 3D Gaussian Splatting renderer executing at 90fps with sub-11ms frame times on mobile XR chipsets.',
          'Developed multi-camera visual-inertial odometry pipeline maintaining spatial anchor drift under 0.2% over 1km travel trajectories.',
          'Secured 2 patents in spatial occlusion calculation and neural depth estimation.',
        ],
      ),
      WorkExperience(
        role: 'Computer Vision Engineer',
        company: 'Visionix Robotics',
        location: 'Turin, Italy',
        period: '2018 — 2021',
        bullets: [
          'Created real-time object detection and 6DoF pose estimation systems for autonomous warehouse sorting robotic arms.',
          'Quantized semantic segmentation models to 8-bit integers, increasing throughput from 18 to 72 FPS on Jetson Xavier hardware.',
        ],
      ),
      WorkExperience(
        role: 'Vision Systems Researcher',
        company: 'Politecnico di Milano Robotics Lab',
        location: 'Milan, Italy',
        period: '2016 — 2018',
        bullets: [
          'Published research on stereo depth fusion and obstacle avoidance in unstructured agricultural environments.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Computer Science and Automation Engineering',
        institution: 'Politecnico di Milano',
        year: '2016',
        details: 'Highest Distinction (110/110 e Lode)',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'FastSplat-XR',
        description: 'Lightweight OpenXR compute shader implementation for rendering dense point splats with dynamic level-of-detail streaming.',
        techStack: ['C++', 'OpenGL / Vulkan', 'OpenXR', 'CUDA'],
      ),
    ],
    certifications: [
      'NVIDIA Jetson Certified Edge AI Developer',
    ],
  ),
  Candidate(
    id: 'CAN-0011',
    candidateNumber: 11,
    name: 'Tariq Mansoor',
    headline: 'Lead Data Platform & Streaming Architect',
    location: 'Dubai, UAE',
    email: 'tariq.mansoor@data-stream.ae',
    phone: '+971 4 391 0021',
    portfolioUrl: 'https://tariqmansoor.cloud',
    githubUrl: 'https://github.com/tmansoor-data',
    matchScore: 87,
    yearsOfExperience: 10,
    category: 'Cloud & Infrastructure',
    previewSnippet:
        'Apache Iceberg, ClickHouse, Apache Flink, and petabyte streaming pipelines handling 80 billion telemetry records daily.',
    summary:
        'Data platform architect with a track record of designing modern lakehouse architectures that scale effortlessly to petabytes. Expert in stateful event streaming (Flink, Kafka), real-time OLAP engines (ClickHouse, DuckDB), and open table formats (Apache Iceberg) with strict schema governance.',
    skills: [
      'Apache Flink',
      'Apache Iceberg',
      'ClickHouse',
      'Apache Kafka',
      'dbt / Trino',
      'Python / PySpark',
      'Scala / Java',
      'Data Governance',
      'AWS EMR / BigQuery',
      'Lakehouse Architecture',
    ],
    experiences: [
      WorkExperience(
        role: 'Director of Data Architecture',
        company: 'Oasis Fintech Group',
        location: 'Dubai, UAE',
        period: '2021 — PRESENT',
        bullets: [
          'Built next-generation streaming financial telemetry lakehouse processing 80 billion messages per day with 2-second ingestion freshness.',
          'Migrated 14 PB of proprietary legacy data warehouse storage to Apache Iceberg and ClickHouse, reducing monthly infrastructure costs by 62%.',
          'Established company-wide data contract standard that decreased upstream schema breaking changes from 14/month to 0.',
        ],
      ),
      WorkExperience(
        role: 'Staff Big Data Engineer',
        company: 'Emirates Telecom Data Labs',
        location: 'Abu Dhabi, UAE',
        period: '2017 — 2021',
        bullets: [
          'Constructed real-time fraud detection pipeline on Flink clusters analyzing 250,000 transactions/second with sub-100ms alerting.',
          'Authored custom Spark SQL connectors optimizing columnar scan pushdowns.',
        ],
      ),
      WorkExperience(
        role: 'Data Warehouse Engineer',
        company: 'Gulf Systems Corp',
        location: 'Dubai, UAE',
        period: '2014 — 2017',
        bullets: [
          'Maintained high-availability PostgreSQL and Hadoop cluster infrastructure for enterprise logistics reporting.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Data Science and Big Data Analytics',
        institution: 'University of Edinburgh',
        year: '2014',
      ),
      Education(
        degree: 'B.S. in Information Systems',
        institution: 'American University of Sharjah',
        year: '2012',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'Iceberg-DeltaSync',
        description: 'High-throughput Rust worker streaming changelog data feeds directly into partitioned Apache Iceberg table snapshots.',
        techStack: ['Rust', 'Apache Arrow', 'Iceberg REST Catalog'],
      ),
    ],
    certifications: [
      'Confluent Certified Event Streaming Architect',
      'Databricks Certified Data Engineer Professional',
    ],
  ),
  Candidate(
    id: 'CAN-0012',
    candidateNumber: 12,
    name: 'Chloe Laurent',
    headline: 'Senior Flutter & Mobile Systems Lead',
    location: 'Paris, France',
    email: 'chloe.laurent@mobile-atelier.fr',
    phone: '+33 1 42 68 55 90',
    portfolioUrl: 'https://chloelaurent.mobile',
    githubUrl: 'https://github.com/claurent-flutter',
    matchScore: 86,
    yearsOfExperience: 8,
    category: 'Mobile & Flutter',
    previewSnippet:
        'Flutter GDE (Google Developer Expert). Custom platform channels, FFI C++ bindings, offline syncing, and pristine 120Hz UI performance.',
    summary:
        'Google Developer Expert in Flutter with deep expertise building enterprise multi-platform applications for iOS, Android, and Web. Master of memory leak diagnosis, Dart FFI native bindings, custom sliver physics, reactive state management (Riverpod / BLoC), and smooth 120Hz rendering pipelines.',
    skills: [
      'Flutter / Dart',
      'Dart FFI (C/C++ Interop)',
      'Custom Slivers & RenderObjects',
      'Riverpod / BLoC',
      'Platform Channels (Swift/Kotlin)',
      'Offline-First & SQLite',
      'Performance Profiling',
      'Flutter Web Architecture',
      'CI/CD for Mobile (Fastlane)',
      'Automated UI Testing',
    ],
    experiences: [
      WorkExperience(
        role: 'Mobile Engineering Lead',
        company: 'Luminary Health',
        location: 'Paris & Remote',
        period: '2021 — PRESENT',
        bullets: [
          'Led mobile engineering team delivering health companion app with 4.9-star rating across 2.4 million iOS and Android installs.',
          'Wrote custom C++ audio analysis engine interfaced via Dart FFI to perform real-time breath acoustics processing with zero battery drain.',
          'Eliminated frame drops across older Android handsets, achieving stable 99.8% jank-free 120Hz frame render rate.',
        ],
      ),
      WorkExperience(
        role: 'Senior Flutter Developer',
        company: 'Fintech Parisienne',
        location: 'Paris, France',
        period: '2018 — 2021',
        bullets: [
          'Spearheaded transition of native iOS/Android codebases into single shared Flutter codebase, saving 18 developer months.',
          'Built biometric authentication module with encrypted hardware keystore backing for compliant payments.',
        ],
      ),
      WorkExperience(
        role: 'iOS Developer',
        company: 'AppStudio France',
        location: 'Lyon, France',
        period: '2016 — 2018',
        bullets: [
          'Built native Swift apps utilizing CoreData, CoreAnimation, and AVFoundation.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Mobile Computing and Human Interactions',
        institution: 'Sorbonne Université',
        year: '2016',
      ),
      Education(
        degree: 'B.S. in Computer Science',
        institution: 'Université Claude Bernard Lyon 1',
        year: '2014',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'SmoothSliver-Flow',
        description: 'Flutter package implementing custom RenderSliver with magnetic snap points and rubber-band header parallax.',
        techStack: ['Flutter', 'Dart', 'Custom RenderObject'],
        link: 'https://github.com/claurent/smooth-sliver',
      ),
    ],
    certifications: [
      'Google Developer Expert (GDE) — Flutter & Dart',
    ],
  ),
  Candidate(
    id: 'CAN-0013',
    candidateNumber: 13,
    name: 'Henrik Lindqvist',
    headline: 'Staff Database Engine & Storage Developer',
    location: 'Stockholm, Sweden',
    email: 'henrik.lindqvist@storage-kernel.se',
    phone: '+46 8 505 21 400',
    portfolioUrl: 'https://hlindqvist.tech',
    githubUrl: 'https://github.com/hlindqvist-db',
    matchScore: 85,
    yearsOfExperience: 13,
    category: 'Systems & Distributed',
    previewSnippet:
        'LSM trees, write-ahead logs, vectorized execution, and NVMe Direct-I/O optimizations. Core contributor to open-source database engines.',
    summary:
        'Systems engineer dedicated to database storage engines, page cache management, and vectorized query execution. 13 years crafting high-performance B-tree and LSM storage layers with deep knowledge of NVMe SSD block characteristics, io_uring asynchronous I/O, and transaction serializability.',
    skills: [
      'C++ (17/20)',
      'Rust',
      'LSM-Trees & B+Trees',
      'io_uring / Linux AIO',
      'Vectorized Query Exec',
      'ACID & MVCC Design',
      'WAL & Crash Recovery',
      'NVMe & SPDK Drivers',
      'Memory Management',
      'Benchmarking & Profiling',
    ],
    experiences: [
      WorkExperience(
        role: 'Staff Storage Engine Engineer',
        company: 'Baltic Storage Engines',
        location: 'Stockholm, Sweden',
        period: '2019 — PRESENT',
        bullets: [
          'Authored high-performance LSM-tree storage engine with Tiered Compaction capable of 12M point lookups/second.',
          'Integrated Linux io_uring asynchronous I/O primitives, reducing thread context switching overhead by 46% during heavy write spikes.',
          'Designed optimistic multi-version concurrency control (MVCC) engine guaranteeing strict snapshot isolation with zero locks.',
        ],
      ),
      WorkExperience(
        role: 'Senior Systems Developer',
        company: 'Nordic DB Systems',
        location: 'Uppsala, Sweden',
        period: '2014 — 2019',
        bullets: [
          'Engineered vectorized columnar filter operators with AVX2 SIMD acceleration for open-source analytics database.',
          'Re-architected buffer pool manager to leverage modern tiered DRAM and PMEM storage hierarchies.',
        ],
      ),
      WorkExperience(
        role: 'C++ Systems Engineer',
        company: 'Ericsson Research',
        location: 'Kista, Sweden',
        period: '2011 — 2014',
        bullets: [
          'Developed embedded telemetry database for telecommunication radio base station hardware.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Computer Science',
        institution: 'KTH Royal Institute of Technology',
        year: '2011',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'Kall-Engine',
        description: 'Embedded key-value store in modern C++ utilizing io_uring and monotonic arena allocators for ultra-low latency flash storage.',
        techStack: ['C++20', 'Linux io_uring', 'Google Benchmark'],
      ),
    ],
    certifications: [
      'Linux Foundation Systems Programming Certified Professional',
    ],
  ),
  Candidate(
    id: 'CAN-0014',
    candidateNumber: 14,
    name: 'Priya Sharma',
    headline: 'Senior NLP & Conversational AI Engineer',
    location: 'Bengaluru, India',
    email: 'priya.sharma@ai-convo.in',
    phone: '+91 80 4112 7650',
    portfolioUrl: 'https://priyasharma.ai',
    githubUrl: 'https://github.com/psharma-nlp',
    matchScore: 84,
    yearsOfExperience: 7,
    category: 'AI & Machine Learning',
    previewSnippet:
        'Fine-tuning reasoning models, multilingual embeddings across 24 Indic languages, and agentic tool-use orchestration.',
    summary:
        'NLP specialist focused on multilingual large language models, agentic workflows, function calling, and structured semantic reasoning. Extensive experience building enterprise AI agents that reliably perform complex multi-step database and API orchestration with tight safety constraints.',
    skills: [
      'Python',
      'PyTorch',
      'LLM Fine-Tuning (LoRA / QLoRA)',
      'LangChain / LlamaIndex',
      'Multilingual NLP',
      'Vector Databases (Milvus, Qdrant)',
      'Agentic Systems & ReAct',
      'Hugging Face Transformers',
      'Prompt Optimization / DSPy',
      'FastAPI & Docker',
    ],
    experiences: [
      WorkExperience(
        role: 'Senior Conversational AI Lead',
        company: 'Indus AI Technologies',
        location: 'Bengaluru, India',
        period: '2022 — PRESENT',
        bullets: [
          'Fine-tuned 13B parameter multilingual foundation models for customer intent comprehension across 14 Indic languages, surpassing GPT-3.5 quality.',
          'Built autonomous agent workflow with DSPy and self-reflection loops, raising structured JSON schema adherence from 82% to 99.7%.',
          'Managed semantic caching system that saved \$45,000 monthly in commercial API token expenditures.',
        ],
      ),
      WorkExperience(
        role: 'Machine Learning Engineer',
        company: 'Cognitive Minds Labs',
        location: 'Hyderabad, India',
        period: '2019 — 2022',
        bullets: [
          'Engineered neural named entity recognition (NER) pipelines for processing legal contracts with 94.2% F1 score.',
          'Deployed scalable microservices on Kubernetes with automated canary rollouts and drift monitoring.',
        ],
      ),
      WorkExperience(
        role: 'Data Science Associate',
        company: 'Tata Consultancy Services',
        location: 'Bengaluru, India',
        period: '2017 — 2019',
        bullets: [
          'Analyzed customer sentiment across social media streams using classical statistical NLP and word2vec embeddings.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.Tech. in Computer Science (Artificial Intelligence)',
        institution: 'Indian Institute of Science (IISc) Bangalore',
        year: '2017',
      ),
      Education(
        degree: 'B.Tech. in Computer Science & Engineering',
        institution: 'National Institute of Technology (NIT) Trichy',
        year: '2015',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'IndicVani-Embed',
        description: 'Sentence transformer model tuned specifically for Indic-English code-switched conversational dialog.',
        techStack: ['Python', 'PyTorch', 'Transformers', 'PEFT'],
      ),
    ],
    certifications: [
      'DeepLearning.AI Generative AI Specialist',
    ],
  ),
  Candidate(
    id: 'CAN-0015',
    candidateNumber: 15,
    name: 'Alexander Cruz',
    headline: 'Senior Performance & Compilers Engineer',
    location: 'Toronto, Canada',
    email: 'alex.cruz@compiler-perf.ca',
    phone: '+1 416 555 8312',
    portfolioUrl: 'https://acruz-perf.dev',
    githubUrl: 'https://github.com/acruz-llvm',
    matchScore: 83,
    yearsOfExperience: 9,
    category: 'Systems & Distributed',
    previewSnippet:
        'LLVM passes, WebAssembly JIT runtimes, dead-code elimination, and register allocation optimizations.',
    summary:
        'Compilers and runtime engineer with background in LLVM backend targets, WebAssembly (Wasm) runtimes, bytecode interpreters, and profile-guided optimization (PGO). Passionate about shaving CPU cycles and dead allocations through AST rewrite passes and link-time optimizations.',
    skills: [
      'LLVM / Clang',
      'WebAssembly (Wasm / WASI)',
      'C++ / Rust',
      'Compilers & Bytecode',
      'JIT & AOT Compilation',
      'Register Allocation',
      'Profile-Guided Optimization',
      'x86 / ARM64 Assembly',
      'Static Analysis Tools',
      'Memory Management',
    ],
    experiences: [
      WorkExperience(
        role: 'Lead Compiler Engineer',
        company: 'WasmSphere Runtime Systems',
        location: 'Toronto & Remote',
        period: '2021 — PRESENT',
        bullets: [
          'Engineered lightweight sandboxed WebAssembly execution engine achieving 92% of native execution speed on serverless cloud nodes.',
          'Built LLVM optimization pass identifying and coalescing redundant memory spill instructions, reducing binary footprint by 19%.',
          'Collaborated on WASI (WebAssembly System Interface) sub-committee standards for secure file and socket capabilities.',
        ],
      ),
      WorkExperience(
        role: 'Senior Tools & Performance Developer',
        company: 'Northern MicroSystems',
        location: 'Waterloo, Canada',
        period: '2017 — 2021',
        bullets: [
          'Improved build times by 40% for large C++ codebase by creating distributed caching compiler wrapper.',
          'Designed static analysis linter that caught 110+ concurrency bugs during continuous integration testing.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.Math. in Computer Science',
        institution: 'University of Waterloo',
        year: '2017',
        details: 'Focus: Automated Compiler Vectorization Passes for Heterogeneous Chips',
      ),
      Education(
        degree: 'B.S. in Software Engineering',
        institution: 'University of Toronto',
        year: '2015',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'MiniJIT-Wasm',
        description: 'Single-pass WebAssembly JIT compiler targeting ARM64 with minimal memory footprint for embedded IoT nodes.',
        techStack: ['Rust', 'ARM64 Assembly', 'Wasm Spec'],
      ),
    ],
    certifications: [
      'ACM SIGPLAN Member',
    ],
  ),
  Candidate(
    id: 'CAN-0016',
    candidateNumber: 16,
    name: 'Nina Kowalski',
    headline: 'Cloud Native Kubernetes Infrastructure Engineer',
    location: 'Warsaw, Poland',
    email: 'nina.kowalski@k8s-infra.pl',
    phone: '+48 22 590 1482',
    portfolioUrl: 'https://kowalski-cloud.io',
    githubUrl: 'https://github.com/nkowalski-k8s',
    matchScore: 82,
    yearsOfExperience: 6,
    category: 'Cloud & Infrastructure',
    previewSnippet:
        'Kubernetes Custom Resource Definitions (CRDs), Cilium eBPF networking, GitOps pipelines, and zero-trust service mesh.',
    summary:
        'Cloud-native platform engineer building resilient developer platforms on top of Kubernetes. Deep knowledge of Cilium CNI, eBPF service mesh routing, Helm/Kustomize templating, automated policy enforcement with Kyverno, and multi-tenant isolation.',
    skills: [
      'Kubernetes / CRDs',
      'Go',
      'Cilium / eBPF Networking',
      'GitOps (ArgoCD, Flux)',
      'Prometheus / OpenTelemetry',
      'Kyverno / OPA Gatekeeper',
      'Terraform',
      'Helm & Kustomize',
      'AWS EKS / GKE',
      'Developer Platforms',
    ],
    experiences: [
      WorkExperience(
        role: 'Senior Platform Engineer',
        company: 'Vistula Cloud Labs',
        location: 'Warsaw, Poland',
        period: '2022 — PRESENT',
        bullets: [
          'Constructed internal developer platform (IDP) enabling 200+ engineers to provision ephemeral staging environments in under 90 seconds.',
          'Migrated network layer to Cilium eBPF, eliminating kube-proxy iptables overhead and accelerating pod-to-pod throughput by 22%.',
          'Enforced zero-trust network policies and mutual TLS across 40 production namespaces with zero application disruptions.',
        ],
      ),
      WorkExperience(
        role: 'DevOps & Cloud Engineer',
        company: 'PolData Solutions',
        location: 'Krakow, Poland',
        period: '2019 — 2022',
        bullets: [
          'Maintained multi-region AWS infrastructure with Terraform, reducing drift incidents to near zero.',
          'Implemented central logging and distributed tracing cluster with OpenTelemetry and Grafana Tempo.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'B.S. in Computer Science & Information Technology',
        institution: 'Warsaw University of Technology',
        year: '2019',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'KubePolicy-Verify',
        description: 'CLI tool validating Kubernetes manifests against security benchmarks before committing to GitOps repositories.',
        techStack: ['Go', 'Kyverno API', 'GitHub Actions'],
      ),
    ],
    certifications: [
      'Certified Kubernetes Application Developer (CKAD)',
      'Certified Kubernetes Administrator (CKA)',
    ],
  ),
  Candidate(
    id: 'CAN-0017',
    candidateNumber: 17,
    name: 'Lucas Moreau',
    headline: 'Staff Frontend & Design Systems Architect',
    location: 'Montreal, Canada',
    email: 'lucas.moreau@frontcraft.ca',
    phone: '+1 514 555 3891',
    portfolioUrl: 'https://lucasmoreau.design',
    githubUrl: 'https://github.com/lmoreau-ui',
    matchScore: 81,
    yearsOfExperience: 9,
    category: 'Full-Stack & Web',
    previewSnippet:
        'Micro-frontends, module federation, headless UI design systems, and web performance optimization at enterprise scale.',
    summary:
        'Frontend architect with a strong foundation in browser internals, rendering pipelines, and modular design systems. Expert in architecting micro-frontend applications with Webpack/Vite module federation, optimizing Core Web Vitals, and writing headless UI component libraries.',
    skills: [
      'TypeScript',
      'React / Next.js',
      'Web Performance & CWV',
      'Design Systems Architecture',
      'Module Federation',
      'CSS Architecture & Tokens',
      'State Management (Zustand)',
      'Micro-Frontends',
      'Vite / Rollup Bundling',
      'Testing (Playwright, Jest)',
    ],
    experiences: [
      WorkExperience(
        role: 'Staff Frontend Architect',
        company: 'Maple Global Commerce',
        location: 'Montreal, Canada',
        period: '2021 — PRESENT',
        bullets: [
          'Led architecture of omnichannel e-commerce storefront generating \$800M in annual transactions with sub-second LCP scores.',
          'Developed headless UI component library adopted across 12 product teams, reducing design-to-production turnaround by 40%.',
          'Spearheaded performance taskforce that improved mobile Core Web Vitals into the 99th percentile across all page templates.',
        ],
      ),
      WorkExperience(
        role: 'Senior Frontend Engineer',
        company: 'Montreal Interactive',
        location: 'Montreal, Canada',
        period: '2017 — 2021',
        bullets: [
          'Architected complex dashboard applications utilizing virtualized lists for rendering 100,000+ data points smoothly.',
          'Implemented end-to-end automated testing with Playwright, catching regressions before production release.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'B.S. in Software Engineering',
        institution: 'McGill University',
        year: '2016',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'Headless-A11y',
        description: 'Zero-style accessible UI primitives with keyboard navigation and ARIA state management for modern web frameworks.',
        techStack: ['TypeScript', 'DOM APIs', 'Vitest'],
      ),
    ],
    certifications: [
      'Meta Frontend Professional Certified',
    ],
  ),
  Candidate(
    id: 'CAN-0018',
    candidateNumber: 18,
    name: 'Aisha Al-Nuaimi',
    headline: 'Quantitative Systems & ML Platform Engineer',
    location: 'Doha, Qatar',
    email: 'aisha.nuaimi@quant-systems.qa',
    phone: '+974 4410 8820',
    portfolioUrl: 'https://aisha-nuaimi.qa',
    githubUrl: 'https://github.com/aisha-quant',
    matchScore: 80,
    yearsOfExperience: 7,
    category: 'AI & Machine Learning',
    previewSnippet:
        'Feature stores, backtesting engines, statistical arbitrage models, and low-latency feature extraction pipelines in Python/C++.',
    summary:
        'Machine learning platform engineer specializing in quantitative feature stores, high-frequency backtesting infrastructure, and statistical learning. Skilled in building reliable real-time streaming feature pipelines using Feast, Redis, and Ray, ensuring zero train-serve feature skew.',
    skills: [
      'Python',
      'C++',
      'Feature Stores (Feast)',
      'Ray / Ray Serve',
      'Time-Series Forecasting',
      'Polars / DuckDB',
      'Kafka / Redis',
      'PyTorch / Scikit-learn',
      'Backtesting Frameworks',
      'Docker & CI/CD',
    ],
    experiences: [
      WorkExperience(
        role: 'Senior ML Platform Engineer',
        company: 'Pearl Capital Quant',
        location: 'Doha, Qatar',
        period: '2022 — PRESENT',
        bullets: [
          'Built quantitative feature store serving 85,000 streaming features per second with sub-5ms lookup latencies.',
          'Engineered vectorized backtesting simulation engine running 10 years of multi-asset market data in under 4 minutes using Polars and Rust.',
          'Eliminated train-serve data leakage across 12 proprietary production trading models.',
        ],
      ),
      WorkExperience(
        role: 'Quantitative Software Developer',
        company: 'Gulf Asset Management',
        location: 'Doha, Qatar',
        period: '2018 — 2022',
        bullets: [
          'Developed automated execution algorithms in C++ for algorithmic order routing.',
          'Constructed automated data cleaning pipeline reconciling market ticks from multiple international liquidity exchanges.',
        ],
      ),
    ],
    education: [
      Education(
        degree: 'M.S. in Computational Finance & Machine Learning',
        institution: 'Imperial College London',
        year: '2018',
      ),
      Education(
        degree: 'B.S. in Computer Science',
        institution: 'Qatar University',
        year: '2016',
      ),
    ],
    projects: [
      ResumeProject(
        name: 'FastFeature-Store',
        description: 'Lightweight in-memory feature caching layer for sub-millisecond model inference with point-in-time correctness guarantees.',
        techStack: ['Python', 'Rust', 'Redis', 'Arrow'],
      ),
    ],
    certifications: [
      'CFA Institute Python for Investment Management',
      'AWS Certified Data Analytics — Specialty',
    ],
  ),
];
