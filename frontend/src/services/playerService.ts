export interface Player {
  id: number;
  name: string;
  position: string;
  rating: number;

  team: {
    id: number;
    name: string;
    shortName: string;
  };
}

export async function getPlayers(): Promise<Player[]> {
  const response = await fetch(
    "http://127.0.0.1:8000/players"
  );

  if (!response.ok) {
    throw new Error("Failed to fetch players");
  }

  return response.json();
}