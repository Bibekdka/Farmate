const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function askAI(message: string) {
  const response = await fetch(`${API_BASE_URL}/api/ai`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error("AI request failed");
  }

  return response.json();
}
