const API_ORIGIN =
  process.env.NEXT_PUBLIC_API_ORIGIN || "http://localhost:8000";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || `${API_ORIGIN}/api`;

export const GITHUB_LOGIN_URL = `${API_ORIGIN}/api/auth/github`;

async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    throw new Error("AUTH_REQUIRED");
  }

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`API error ${response.status}:`, errorText);
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

export async function fetchCurrentUser() {
  return apiFetch("/auth/me");
}

export async function logout() {
  return apiFetch("/auth/logout", { method: "POST" });
}

export async function fetchProfile(refresh = false) {
  const suffix = refresh ? "?refresh=true" : "";
  return apiFetch(`/profile${suffix}`);
}

export async function fetchRepositories(refresh = false) {
  const suffix = refresh ? "?refresh=true" : "";
  return apiFetch(`/repos${suffix}`);
}

export async function fetchRepositoryDetail(id: number | string) {
  return apiFetch(`/repos/${id}`);
}

export async function uploadResume(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/career/resume/upload`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });

  if (response.status === 401) {
    throw new Error("AUTH_REQUIRED");
  }

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Resume upload failed:", errorText);
    throw new Error("Failed to upload and analyze resume");
  }

  return response.json();
}

export async function analyzeJobDescription(
  title: string,
  company: string,
  jobText: string
) {
  return apiFetch("/career/jobs/analyze", {
    method: "POST",
    body: JSON.stringify({
      title,
      company,
      job_text: jobText,
    }),
  });
}

export async function fetchJobAnalysisHistory() {
  return apiFetch("/career/jobs/history");
}

export async function fetchRoadmap(
  targetRole: string = "Backend Engineer",
  refresh = false,
  jobId?: number
) {
  const params = new URLSearchParams();

  if (jobId !== undefined) {
    params.set("job_id", String(jobId));
  } else {
    params.set("target_role", targetRole);
  }

  if (refresh) {
    params.set("refresh", "true");
  }

  return apiFetch(`/roadmap?${params.toString()}`);
}

export async function sendChatMessage(message: string) {
  return apiFetch("/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
    }),
  });
}

export async function fetchChatHistory() {
  return apiFetch("/chat/history");
}