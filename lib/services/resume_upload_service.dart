import 'package:file_picker/file_picker.dart';
import '../models/candidate.dart';

class ResumeUploadService {
  /// Cleans a filename like 'Resume_Sarah_Jenkins_2026.pdf' into 'Sarah Jenkins'
  static String cleanCandidateName(String filename) {
    var name = filename.replaceAll(RegExp(r'\.pdf$', caseSensitive: false), '');
    name = name.replaceAll(RegExp(r'[_\-\.]'), ' ').trim();
    // Remove typical noise words in resume filenames
    name = name
        .replaceAll(
          RegExp(
            r'\b(resume|cv|dossier|document|profile|2024|2025|2026|final|v1|v2|v3)\b',
            caseSensitive: false,
          ),
          '',
        )
        .trim();

    if (name.isEmpty) {
      return 'Uploaded Candidate';
    }

    // Capitalize words
    final parts = name
        .split(' ')
        .where((s) => s.isNotEmpty)
        .map((s) => s[0].toUpperCase() + s.substring(1))
        .toList();

    if (parts.length == 1 && RegExp(r'^\d+$').hasMatch(parts.first)) {
      return 'Candidate (Dossier ${parts.first})';
    }

    return parts.join(' ');
  }

  /// Generates a realistic mock Candidate instance from an uploaded file
  static Candidate createMockCandidateFromUpload({
    required String fileName,
    required int fileSize,
    required int index,
    String defaultCategory = 'Full-Stack & Web',
  }) {
    final cleanName = cleanCandidateName(fileName);
    final emailHandle = cleanName.toLowerCase().replaceAll(' ', '.');
    final formattedScore = 84 + ((index * 7) % 13); // Generates varied scores: 84 - 96%
    final expYears = 4 + ((index * 2) % 9); // 4 - 12 years

    // Varied categories for newly uploaded resumes
    final categories = [
      'Full-Stack & Web',
      'AI & Machine Learning',
      'Systems & Distributed',
      'Creative & Frontend',
      'Cloud & Infrastructure',
      'Mobile & Flutter',
      'Security & Cloud',
    ];
    final assignedCategory = categories[index % categories.length];

    // Varied skills tailored to category
    final List<String> skills;
    final String headline;
    if (assignedCategory.contains('AI')) {
      headline = 'Machine Learning Engineer · Applied Research';
      skills = ['PyTorch', 'Transformers', 'LLM Tuning', 'CUDA', 'Python', 'MLOps'];
    } else if (assignedCategory.contains('Systems')) {
      headline = 'Systems & Infrastructure Engineer';
      skills = ['Rust', 'Distributed Systems', 'gRPC', 'Kubernetes', 'Go', 'Linux Kernel'];
    } else if (assignedCategory.contains('Creative')) {
      headline = 'Senior Creative Technologist & UI Engineer';
      skills = ['WebGL', 'GLSL Shaders', 'Three.js', 'Flutter', 'TypeScript', 'Design Systems'];
    } else if (assignedCategory.contains('Mobile')) {
      headline = 'Senior Mobile Architect · Flutter / Native';
      skills = ['Flutter', 'Dart', 'Swift', 'Kotlin', 'Clean Architecture', 'CI/CD'];
    } else {
      headline = 'Principal Full-Stack Engineer · Distributed Web';
      skills = ['TypeScript', 'Flutter Web', 'PostgreSQL', 'Go', 'Docker', 'GraphQL'];
    }

    final fileSizeKb = (fileSize / 1024).toStringAsFixed(1);

    return Candidate(
      id: 'uploaded_${DateTime.now().millisecondsSinceEpoch}_$index',
      candidateNumber: index,
      name: cleanName,
      headline: headline,
      location: 'San Francisco, CA (Remote)',
      email: '$emailHandle@archival.dev',
      phone: '+1 (555) ${100 + index}-${2000 + index}',
      portfolioUrl: 'https://$emailHandle.dev',
      githubUrl: 'https://github.com/$emailHandle',
      summary:
          'Uploaded document dossier ($fileName · $fileSizeKb KB). Experienced engineering profile spanning $expYears years of technical leadership, architecting resilient distributed platforms, and delivering high-impact product experiences.',
      matchScore: formattedScore,
      yearsOfExperience: expYears,
      category: assignedCategory,
      skills: skills,
      experiences: [
        WorkExperience(
          role: headline.split('·').first.trim(),
          company: 'Nexus Tech Labs',
          location: 'San Francisco, CA',
          period: '2022 — Present',
          bullets: [
            'Led technical architecture and engineering delivery across core systems.',
            'Optimized data processing throughput by 38% using asynchronous pipelines.',
            'Mentored cross-functional engineering teams on code quality and architectural standards.',
          ],
        ),
        WorkExperience(
          role: 'Senior Software Engineer',
          company: 'Aether Systems',
          location: 'Remote',
          period: '2019 — 2022',
          bullets: [
            'Designed and maintained high-reliability services handling millions of daily operations.',
            'Integrated automated test harnesses reducing deployment defects by 42%.',
          ],
        ),
      ],
      education: [
        Education(
          degree: 'B.S. in Computer Science & Engineering',
          institution: 'State Technological Institute',
          year: '2018',
          details: 'Summa Cum Laude · Algorithms & Distributed Systems Focus',
        ),
      ],
      projects: [
        ResumeProject(
          name: 'HyperScale Engine',
          description: 'High-throughput event aggregation engine designed for low-latency telemetry.',
          techStack: skills.take(3).toList(),
          link: 'https://github.com/$emailHandle/hyperscale',
        ),
      ],
      certifications: [
        'Cloud Solutions Architect Certified',
        'Advanced Systems Performance Engineering',
      ],
      previewSnippet:
          'Uploaded dossier processed from $fileName. Technical background emphasizes $expYears years in $assignedCategory, high-throughput systems, and core competencies in ${skills.take(3).join(', ')}.',
      isShortlisted: false,
    );
  }

  /// Opens the native multi-file PDF picker on Flutter Web / Desktop
  /// and returns freshly created mock Candidate objects for the carousel.
  /// Automatically filters out duplicates against [existingNames] or duplicate files.
  static Future<List<Candidate>> pickAndCreateCandidates({
    required int currentTotalCount,
    String defaultCategory = 'Full-Stack & Web',
    Set<String>? existingNames,
  }) async {
    try {
      final files = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
      );

      if (files.isEmpty) {
        return [];
      }

      final List<Candidate> newCandidates = [];
      final Set<String> seenInBatch = <String>{};

      for (int i = 0; i < files.length; i++) {
        final file = files[i];
        final cleanName = cleanCandidateName(file.name);
        final lowerName = cleanName.toLowerCase();

        // Prevent duplicate candidates within this batch or already uploaded
        if (seenInBatch.contains(lowerName)) continue;
        if (existingNames != null && existingNames.contains(lowerName)) continue;

        seenInBatch.add(lowerName);

        final fileSize = file.lengthSync() ?? 102400;

        final candidate = createMockCandidateFromUpload(
          fileName: file.name,
          fileSize: fileSize,
          index: currentTotalCount + newCandidates.length + 1,
          defaultCategory: defaultCategory,
        );
        newCandidates.add(candidate);
      }
      return newCandidates;
    } catch (e) {
      return [];
    }
  }
}
