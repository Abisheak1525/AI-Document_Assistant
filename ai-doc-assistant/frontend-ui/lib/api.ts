// frontend-ui/lib/api.ts
export const chatWithAI = async (query: string) => {
  const response = await fetch("http://localhost:8080/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  
  if (!response.ok) throw new Error("Failed to connect to backend");
  return response.json();
};