/** Client helpers for the authenticated brand-document knowledge base. */

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export interface UploadedDocument {
  document_id: string;
  filename: string;
  file_type: string;
  chunk_count: number;
  uploaded_at: string;
  campaign_id: string | null;
}

export async function uploadDocuments(
  files: File[],
  campaignId?: string,
): Promise<UploadedDocument[]> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  if (campaignId) {
    formData.append("campaign_id", campaignId);
  }

  const response = await fetch(`${API_BASE}/documents/`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error(await getResponseError(response));
  }
  return (await response.json()) as UploadedDocument[];
}

async function getResponseError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") return payload.detail;
  } catch {
    // Use the HTTP status when the error response has no JSON body.
  }
  return `Document upload failed (HTTP ${response.status}).`;
}
