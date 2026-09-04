export interface League {
  id: number;
  name: string;
  country: string;
  type: string;
  logoUrl: string;
  flagUrl: string;
}


export async function getLeagues(
  season = 2026
): Promise<League[]> {

  const response = await fetch(
    `http://127.0.0.1:8000/leagues?season=${season}`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch leagues"
    );
  }

  return response.json();
}