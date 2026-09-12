class WorkExperience {
  final String role;
  final String company;
  final String location;
  final String period;
  final List<String> bullets;

  const WorkExperience({
    required this.role,
    required this.company,
    required this.location,
    required this.period,
    required this.bullets,
  });

  Map<String, dynamic> toJson() => {
    'role': role,
    'company': company,
    'location': location,
    'period': period,
    'bullets': bullets,
  };

  factory WorkExperience.fromJson(Map<String, dynamic> json) => WorkExperience(
    role: json['role'] as String,
    company: json['company'] as String,
    location: json['location'] as String,
    period: json['period'] as String,
    bullets: List<String>.from(json['bullets'] as List),
  );
}

class Education {
  final String degree;
  final String institution;
  final String year;
  final String? details;

  const Education({
    required this.degree,
    required this.institution,
    required this.year,
    this.details,
  });

  Map<String, dynamic> toJson() => {
    'degree': degree,
    'institution': institution,
    'year': year,
    'details': details,
  };

  factory Education.fromJson(Map<String, dynamic> json) => Education(
    degree: json['degree'] as String,
    institution: json['institution'] as String,
    year: json['year'] as String,
    details: json['details'] as String?,
  );
}

class ResumeProject {
  final String name;
  final String description;
  final List<String> techStack;
  final String? link;

  const ResumeProject({
    required this.name,
    required this.description,
    required this.techStack,
    this.link,
  });

  Map<String, dynamic> toJson() => {
    'name': name,
    'description': description,
    'techStack': techStack,
    'link': link,
  };

  factory ResumeProject.fromJson(Map<String, dynamic> json) => ResumeProject(
    name: json['name'] as String,
    description: json['description'] as String,
    techStack: List<String>.from(json['techStack'] as List),
    link: json['link'] as String?,
  );
}

class Candidate {
  final String id;
  final int candidateNumber;
  final String name;
  final String headline;
  final String location;
  final String email;
  final String phone;
  final String portfolioUrl;
  final String githubUrl;
  final String summary;
  final int matchScore; // Percentage: e.g. 96
  final int yearsOfExperience;
  final String category; // e.g. "Systems & Distributed", "AI & ML", "Creative & Frontend", etc.
  final List<String> skills;
  final List<WorkExperience> experiences;
  final List<Education> education;
  final List<ResumeProject> projects;
  final List<String> certifications;
  final String previewSnippet;
  final bool isShortlisted;

  const Candidate({
    required this.id,
    required this.candidateNumber,
    required this.name,
    required this.headline,
    required this.location,
    required this.email,
    required this.phone,
    required this.portfolioUrl,
    required this.githubUrl,
    required this.summary,
    required this.matchScore,
    required this.yearsOfExperience,
    required this.category,
    required this.skills,
    required this.experiences,
    required this.education,
    required this.projects,
    required this.certifications,
    required this.previewSnippet,
    this.isShortlisted = false,
  });

  String get formattedNumber => '#${candidateNumber.toString().padLeft(2, '0')}';

  Candidate copyWith({
    String? id,
    int? candidateNumber,
    String? name,
    String? headline,
    String? location,
    String? email,
    String? phone,
    String? portfolioUrl,
    String? githubUrl,
    String? summary,
    int? matchScore,
    int? yearsOfExperience,
    String? category,
    List<String>? skills,
    List<WorkExperience>? experiences,
    List<Education>? education,
    List<ResumeProject>? projects,
    List<String>? certifications,
    String? previewSnippet,
    bool? isShortlisted,
  }) {
    return Candidate(
      id: id ?? this.id,
      candidateNumber: candidateNumber ?? this.candidateNumber,
      name: name ?? this.name,
      headline: headline ?? this.headline,
      location: location ?? this.location,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      portfolioUrl: portfolioUrl ?? this.portfolioUrl,
      githubUrl: githubUrl ?? this.githubUrl,
      summary: summary ?? this.summary,
      matchScore: matchScore ?? this.matchScore,
      yearsOfExperience: yearsOfExperience ?? this.yearsOfExperience,
      category: category ?? this.category,
      skills: skills ?? this.skills,
      experiences: experiences ?? this.experiences,
      education: education ?? this.education,
      projects: projects ?? this.projects,
      certifications: certifications ?? this.certifications,
      previewSnippet: previewSnippet ?? this.previewSnippet,
      isShortlisted: isShortlisted ?? this.isShortlisted,
    );
  }
}
