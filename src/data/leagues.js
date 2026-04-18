export const leaguesData = {
  premierLeague: {
    leagueInfo: {
      id: "premierLeague",
      name: "Premier League",
      country: "England",
      season: "2025/26",
      currentMatchweek: 32
    },

    standings: [
      { position: 1, teamId: "arsenal", teamName: "Arsenal", played: 31, goalDifference: 29, points: 72 },
      { position: 2, teamId: "liverpool", teamName: "Liverpool", played: 31, goalDifference: 25, points: 69 },
      { position: 3, teamId: "manCity", teamName: "Manchester City", played: 31, goalDifference: 23, points: 67 },
      { position: 4, teamId: "chelsea", teamName: "Chelsea", played: 31, goalDifference: 16, points: 61 },
      { position: 5, teamId: "newcastle", teamName: "Newcastle United", played: 31, goalDifference: 12, points: 58 }
    ],

    teamRatings: [
      { teamId: "arsenal", teamName: "Arsenal", powerRank: 8.8, luckRank: 6.7, xg: 2.05, gaAverage: 0.88, recentRating: 8.4, homeRating: 8.9, awayRating: 8.1, winProbability: 0.64 },
      { teamId: "liverpool", teamName: "Liverpool", powerRank: 8.6, luckRank: 6.2, xg: 1.98, gaAverage: 0.95, recentRating: 8.2, homeRating: 8.8, awayRating: 7.9, winProbability: 0.60 },
      { teamId: "manCity", teamName: "Manchester City", powerRank: 8.5, luckRank: 7.0, xg: 1.96, gaAverage: 0.97, recentRating: 8.1, homeRating: 8.7, awayRating: 8.0, winProbability: 0.58 },
      { teamId: "chelsea", teamName: "Chelsea", powerRank: 7.9, luckRank: 5.8, xg: 1.63, gaAverage: 1.09, recentRating: 7.5, homeRating: 8.1, awayRating: 7.3, winProbability: 0.49 },
      { teamId: "newcastle", teamName: "Newcastle United", powerRank: 7.7, luckRank: 6.3, xg: 1.57, gaAverage: 1.15, recentRating: 7.8, homeRating: 8.0, awayRating: 7.2, winProbability: 0.46 }
    ],

    featuredGame: {
      matchId: "pl32-arsenal-liverpool",
      matchweek: 32,
      date: "2026-04-18",
      time: "12:30 PM",
      team1Id: "arsenal",
      team1: "Arsenal",
      team2Id: "liverpool",
      team2: "Liverpool",
      venue: "Emirates Stadium",
      status: "upcoming",
      odds: { team1Win: 2.05, draw: 3.45, team2Win: 3.35 },
      comparisons: {
        team1Power: 8.8,
        team2Power: 8.6,
        team1Luck: 6.7,
        team2Luck: 6.2,
        team1Recent: 8.4,
        team2Recent: 8.2,
        team1HomeAway: 8.9,
        team2HomeAway: 7.9
      }
    },

    upcomingMatchweek: {
      matchweek: 32,
      games: [
        { matchId: "pl32-arsenal-liverpool", team1: "Arsenal", team2: "Liverpool", time: "12:30 PM", date: "2026-04-18", status: "upcoming" },
        { matchId: "pl32-manCity-tottenham", team1: "Manchester City", team2: "Tottenham", time: "3:00 PM", date: "2026-04-18", status: "upcoming" },
        { matchId: "pl32-chelsea-wolves", team1: "Chelsea", team2: "Wolves", time: "5:30 PM", date: "2026-04-18", status: "upcoming" },
        { matchId: "pl32-newcastle-astonVilla", team1: "Newcastle United", team2: "Aston Villa", time: "8:00 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "pl32-manUnited-everton", team1: "Manchester United", team2: "Everton", time: "10:30 AM", date: "2026-04-19", status: "upcoming" }
      ]
    },

    previousMatchweeks: [
      {
        matchweek: 31,
        games: [
          { matchId: "pl31-arsenal-fulham", team1: "Arsenal", team2: "Fulham", time: "2:00 PM", date: "2026-04-11", status: "finished", score: { team1: 2, team2: 0 } },
          { matchId: "pl31-liverpool-brentford", team1: "Liverpool", team2: "Brentford", time: "4:30 PM", date: "2026-04-11", status: "finished", score: { team1: 3, team2: 1 } }
        ]
      }
    ]
  },

  laLiga: {
    leagueInfo: {
      id: "laLiga",
      name: "La Liga",
      country: "Spain",
      season: "2025/26",
      currentMatchweek: 32
    },

    standings: [
      { position: 1, teamId: "realMadrid", teamName: "Real Madrid", played: 31, goalDifference: 31, points: 74 },
      { position: 2, teamId: "barcelona", teamName: "Barcelona", played: 31, goalDifference: 27, points: 71 },
      { position: 3, teamId: "atleticoMadrid", teamName: "Atletico Madrid", played: 31, goalDifference: 20, points: 66 },
      { position: 4, teamId: "athleticClub", teamName: "Athletic Club", played: 31, goalDifference: 14, points: 60 },
      { position: 5, teamId: "realSociedad", teamName: "Real Sociedad", played: 31, goalDifference: 10, points: 56 }
    ],

    teamRatings: [
      { teamId: "realMadrid", teamName: "Real Madrid", powerRank: 8.9, luckRank: 6.6, xg: 2.12, gaAverage: 0.83, recentRating: 8.5, homeRating: 9.0, awayRating: 8.2, winProbability: 0.66 },
      { teamId: "barcelona", teamName: "Barcelona", powerRank: 8.7, luckRank: 6.1, xg: 2.01, gaAverage: 0.91, recentRating: 8.3, homeRating: 8.8, awayRating: 8.0, winProbability: 0.62 },
      { teamId: "atleticoMadrid", teamName: "Atletico Madrid", powerRank: 8.2, luckRank: 6.4, xg: 1.72, gaAverage: 0.94, recentRating: 7.9, homeRating: 8.4, awayRating: 7.7, winProbability: 0.54 },
      { teamId: "athleticClub", teamName: "Athletic Club", powerRank: 7.8, luckRank: 6.0, xg: 1.48, gaAverage: 1.01, recentRating: 7.6, homeRating: 8.1, awayRating: 7.2, winProbability: 0.48 },
      { teamId: "realSociedad", teamName: "Real Sociedad", powerRank: 7.6, luckRank: 5.9, xg: 1.42, gaAverage: 1.06, recentRating: 7.4, homeRating: 7.8, awayRating: 7.1, winProbability: 0.44 }
    ],

    featuredGame: {
      matchId: "ll32-realMadrid-atleticoMadrid",
      matchweek: 32,
      date: "2026-04-18",
      time: "2:00 PM",
      team1Id: "realMadrid",
      team1: "Real Madrid",
      team2Id: "atleticoMadrid",
      team2: "Atletico Madrid",
      venue: "Santiago Bernabeu",
      status: "upcoming",
      odds: { team1Win: 1.95, draw: 3.40, team2Win: 3.85 },
      comparisons: {
        team1Power: 8.9,
        team2Power: 8.2,
        team1Luck: 6.6,
        team2Luck: 6.4,
        team1Recent: 8.5,
        team2Recent: 7.9,
        team1HomeAway: 9.0,
        team2HomeAway: 7.7
      }
    },

    upcomingMatchweek: {
      matchweek: 32,
      games: [
        { matchId: "ll32-realMadrid-atleticoMadrid", team1: "Real Madrid", team2: "Atletico Madrid", time: "2:00 PM", date: "2026-04-18", status: "upcoming" },
        { matchId: "ll32-barcelona-valencia", team1: "Barcelona", team2: "Valencia", time: "4:15 PM", date: "2026-04-18", status: "upcoming" },
        { matchId: "ll32-athleticClub-sevilla", team1: "Athletic Club", team2: "Sevilla", time: "8:00 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "ll32-realSociedad-betis", team1: "Real Sociedad", team2: "Real Betis", time: "10:30 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "ll32-villarreal-girona", team1: "Villarreal", team2: "Girona", time: "1:00 PM", date: "2026-04-19", status: "upcoming" }
      ]
    },

    previousMatchweeks: [
      {
        matchweek: 31,
        games: [
          { matchId: "ll31-realMadrid-getafe", team1: "Real Madrid", team2: "Getafe", time: "3:00 PM", date: "2026-04-12", status: "finished", score: { team1: 2, team2: 1 } },
          { matchId: "ll31-barcelona-villarreal", team1: "Barcelona", team2: "Villarreal", time: "5:30 PM", date: "2026-04-12", status: "finished", score: { team1: 3, team2: 0 } }
        ]
      }
    ]
  },

  serieA: {
    leagueInfo: {
      id: "serieA",
      name: "Serie A",
      country: "Italy",
      season: "2025/26",
      currentMatchweek: 32
    },

    standings: [
      { position: 1, teamId: "inter", teamName: "Inter", played: 31, goalDifference: 30, points: 73 },
      { position: 2, teamId: "juventus", teamName: "Juventus", played: 31, goalDifference: 21, points: 68 },
      { position: 3, teamId: "milan", teamName: "AC Milan", played: 31, goalDifference: 18, points: 65 },
      { position: 4, teamId: "napoli", teamName: "Napoli", played: 31, goalDifference: 15, points: 61 },
      { position: 5, teamId: "roma", teamName: "Roma", played: 31, goalDifference: 11, points: 57 }
    ],

    teamRatings: [
      { teamId: "inter", teamName: "Inter", powerRank: 8.8, luckRank: 6.5, xg: 2.03, gaAverage: 0.84, recentRating: 8.4, homeRating: 8.9, awayRating: 8.1, winProbability: 0.65 },
      { teamId: "juventus", teamName: "Juventus", powerRank: 8.3, luckRank: 6.8, xg: 1.71, gaAverage: 0.89, recentRating: 8.0, homeRating: 8.4, awayRating: 7.8, winProbability: 0.57 },
      { teamId: "milan", teamName: "AC Milan", powerRank: 8.1, luckRank: 6.0, xg: 1.69, gaAverage: 0.97, recentRating: 7.8, homeRating: 8.2, awayRating: 7.6, winProbability: 0.53 },
      { teamId: "napoli", teamName: "Napoli", powerRank: 7.9, luckRank: 5.7, xg: 1.58, gaAverage: 1.03, recentRating: 7.6, homeRating: 8.0, awayRating: 7.4, winProbability: 0.49 },
      { teamId: "roma", teamName: "Roma", powerRank: 7.6, luckRank: 6.1, xg: 1.44, gaAverage: 1.07, recentRating: 7.4, homeRating: 7.8, awayRating: 7.1, winProbability: 0.45 }
    ],

    featuredGame: {
      matchId: "sa32-inter-milan",
      matchweek: 32,
      date: "2026-04-19",
      time: "2:45 PM",
      team1Id: "inter",
      team1: "Inter",
      team2Id: "milan",
      team2: "AC Milan",
      venue: "San Siro",
      status: "upcoming",
      odds: { team1Win: 2.10, draw: 3.20, team2Win: 3.50 },
      comparisons: {
        team1Power: 8.8,
        team2Power: 8.1,
        team1Luck: 6.5,
        team2Luck: 6.0,
        team1Recent: 8.4,
        team2Recent: 7.8,
        team1HomeAway: 8.9,
        team2HomeAway: 7.6
      }
    },

    upcomingMatchweek: {
      matchweek: 32,
      games: [
        { matchId: "sa32-inter-milan", team1: "Inter", team2: "AC Milan", time: "2:45 PM", date: "2026-04-19", status: "upcoming" },
        { matchId: "sa32-juventus-lazio", team1: "Juventus", team2: "Lazio", time: "9:00 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "sa32-napoli-fiorentina", team1: "Napoli", team2: "Fiorentina", time: "12:00 PM", date: "2026-04-19", status: "upcoming" },
        { matchId: "sa32-roma-bologna", team1: "Roma", team2: "Bologna", time: "5:00 PM", date: "2026-04-19", status: "upcoming" },
        { matchId: "sa32-atalanta-torino", team1: "Atalanta", team2: "Torino", time: "7:45 PM", date: "2026-04-19", status: "upcoming" }
      ]
    },

    previousMatchweeks: [
      {
        matchweek: 31,
        games: [
          { matchId: "sa31-inter-udinese", team1: "Inter", team2: "Udinese", time: "1:45 PM", date: "2026-04-12", status: "finished", score: { team1: 2, team2: 1 } },
          { matchId: "sa31-juventus-roma", team1: "Juventus", team2: "Roma", time: "4:00 PM", date: "2026-04-12", status: "finished", score: { team1: 1, team2: 1 } }
        ]
      }
    ]
  },

  bundesliga: {
    leagueInfo: {
      id: "bundesliga",
      name: "Bundesliga",
      country: "Germany",
      season: "2025/26",
      currentMatchweek: 30
    },

    standings: [
      { position: 1, teamId: "bayern", teamName: "Bayern Munich", played: 29, goalDifference: 35, points: 68 },
      { position: 2, teamId: "leverkusen", teamName: "Bayer Leverkusen", played: 29, goalDifference: 29, points: 64 },
      { position: 3, teamId: "dortmund", teamName: "Borussia Dortmund", played: 29, goalDifference: 17, points: 57 },
      { position: 4, teamId: "leipzig", teamName: "RB Leipzig", played: 29, goalDifference: 15, points: 55 },
      { position: 5, teamId: "frankfurt", teamName: "Eintracht Frankfurt", played: 29, goalDifference: 9, points: 50 }
    ],

    teamRatings: [
      { teamId: "bayern", teamName: "Bayern Munich", powerRank: 9.0, luckRank: 6.3, xg: 2.29, gaAverage: 0.86, recentRating: 8.7, homeRating: 9.1, awayRating: 8.4, winProbability: 0.68 },
      { teamId: "leverkusen", teamName: "Bayer Leverkusen", powerRank: 8.7, luckRank: 6.5, xg: 2.06, gaAverage: 0.90, recentRating: 8.4, homeRating: 8.8, awayRating: 8.1, winProbability: 0.63 },
      { teamId: "dortmund", teamName: "Borussia Dortmund", powerRank: 8.0, luckRank: 6.1, xg: 1.73, gaAverage: 1.08, recentRating: 7.7, homeRating: 8.2, awayRating: 7.4, winProbability: 0.51 },
      { teamId: "leipzig", teamName: "RB Leipzig", powerRank: 7.9, luckRank: 5.8, xg: 1.67, gaAverage: 1.04, recentRating: 7.6, homeRating: 8.1, awayRating: 7.5, winProbability: 0.49 },
      { teamId: "frankfurt", teamName: "Eintracht Frankfurt", powerRank: 7.4, luckRank: 6.0, xg: 1.41, gaAverage: 1.18, recentRating: 7.2, homeRating: 7.7, awayRating: 6.9, winProbability: 0.43 }
    ],

    featuredGame: {
      matchId: "bl30-bayern-leverkusen",
      matchweek: 30,
      date: "2026-04-18",
      time: "11:30 AM",
      team1Id: "bayern",
      team1: "Bayern Munich",
      team2Id: "leverkusen",
      team2: "Bayer Leverkusen",
      venue: "Allianz Arena",
      status: "upcoming",
      odds: { team1Win: 1.92, draw: 3.65, team2Win: 3.75 },
      comparisons: {
        team1Power: 9.0,
        team2Power: 8.7,
        team1Luck: 6.3,
        team2Luck: 6.5,
        team1Recent: 8.7,
        team2Recent: 8.4,
        team1HomeAway: 9.1,
        team2HomeAway: 8.1
      }
    },

    upcomingMatchweek: {
      matchweek: 30,
      games: [
        { matchId: "bl30-bayern-leverkusen", team1: "Bayern Munich", team2: "Bayer Leverkusen", time: "11:30 AM", date: "2026-04-18", status: "upcoming" },
        { matchId: "bl30-dortmund-mainz", team1: "Borussia Dortmund", team2: "Mainz", time: "2:30 PM", date: "2026-04-18", status: "upcoming" },
        { matchId: "bl30-leipzig-freiburg", team1: "RB Leipzig", team2: "Freiburg", time: "8:30 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "bl30-frankfurt-stuttgart", team1: "Eintracht Frankfurt", team2: "Stuttgart", time: "10:30 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "bl30-wolfsburg-hoffenheim", team1: "Wolfsburg", team2: "Hoffenheim", time: "12:30 PM", date: "2026-04-19", status: "upcoming" }
      ]
    },

    previousMatchweeks: [
      {
        matchweek: 29,
        games: [
          { matchId: "bl29-bayern-augsburg", team1: "Bayern Munich", team2: "Augsburg", time: "2:30 PM", date: "2026-04-11", status: "finished", score: { team1: 4, team2: 1 } },
          { matchId: "bl29-leverkusen-koln", team1: "Bayer Leverkusen", team2: "Koln", time: "2:30 PM", date: "2026-04-11", status: "finished", score: { team1: 2, team2: 0 } }
        ]
      }
    ]
  },

  ligue1: {
    leagueInfo: {
      id: "ligue1",
      name: "Ligue 1",
      country: "France",
      season: "2025/26",
      currentMatchweek: 30
    },

    standings: [
      { position: 1, teamId: "psg", teamName: "PSG", played: 29, goalDifference: 38, points: 71 },
      { position: 2, teamId: "marseille", teamName: "Marseille", played: 29, goalDifference: 19, points: 61 },
      { position: 3, teamId: "monaco", teamName: "Monaco", played: 29, goalDifference: 17, points: 58 },
      { position: 4, teamId: "lille", teamName: "Lille", played: 29, goalDifference: 13, points: 55 },
      { position: 5, teamId: "nice", teamName: "Nice", played: 29, goalDifference: 9, points: 52 }
    ],

    teamRatings: [
      { teamId: "psg", teamName: "PSG", powerRank: 9.1, luckRank: 6.9, xg: 2.34, gaAverage: 0.79, recentRating: 8.8, homeRating: 9.2, awayRating: 8.5, winProbability: 0.71 },
      { teamId: "marseille", teamName: "Marseille", powerRank: 8.0, luckRank: 6.0, xg: 1.61, gaAverage: 0.98, recentRating: 7.7, homeRating: 8.2, awayRating: 7.4, winProbability: 0.52 },
      { teamId: "monaco", teamName: "Monaco", powerRank: 7.9, luckRank: 5.9, xg: 1.58, gaAverage: 1.03, recentRating: 7.6, homeRating: 8.0, awayRating: 7.4, winProbability: 0.50 },
      { teamId: "lille", teamName: "Lille", powerRank: 7.6, luckRank: 6.1, xg: 1.45, gaAverage: 1.05, recentRating: 7.3, homeRating: 7.8, awayRating: 7.1, winProbability: 0.45 },
      { teamId: "nice", teamName: "Nice", powerRank: 7.4, luckRank: 5.8, xg: 1.39, gaAverage: 1.08, recentRating: 7.2, homeRating: 7.6, awayRating: 6.9, winProbability: 0.42 }
    ],

    featuredGame: {
      matchId: "l130-psg-marseille",
      matchweek: 30,
      date: "2026-04-19",
      time: "2:45 PM",
      team1Id: "psg",
      team1: "PSG",
      team2Id: "marseille",
      team2: "Marseille",
      venue: "Parc des Princes",
      status: "upcoming",
      odds: { team1Win: 1.72, draw: 3.90, team2Win: 4.85 },
      comparisons: {
        team1Power: 9.1,
        team2Power: 8.0,
        team1Luck: 6.9,
        team2Luck: 6.0,
        team1Recent: 8.8,
        team2Recent: 7.7,
        team1HomeAway: 9.2,
        team2HomeAway: 7.4
      }
    },

    upcomingMatchweek: {
      matchweek: 30,
      games: [
        { matchId: "l130-psg-marseille", team1: "PSG", team2: "Marseille", time: "2:45 PM", date: "2026-04-19", status: "upcoming" },
        { matchId: "l130-monaco-rennes", team1: "Monaco", team2: "Rennes", time: "9:00 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "l130-lille-lens", team1: "Lille", team2: "Lens", time: "11:15 AM", date: "2026-04-19", status: "upcoming" },
        { matchId: "l130-nice-lyon", team1: "Nice", team2: "Lyon", time: "1:30 PM", date: "2026-04-19", status: "upcoming" },
        { matchId: "l130-strasbourg-brest", team1: "Strasbourg", team2: "Brest", time: "4:00 PM", date: "2026-04-19", status: "upcoming" }
      ]
    },

    previousMatchweeks: [
      {
        matchweek: 29,
        games: [
          { matchId: "l129-psg-nantes", team1: "PSG", team2: "Nantes", time: "3:00 PM", date: "2026-04-12", status: "finished", score: { team1: 3, team2: 0 } },
          { matchId: "l129-marseille-reims", team1: "Marseille", team2: "Reims", time: "5:00 PM", date: "2026-04-12", status: "finished", score: { team1: 2, team2: 1 } }
        ]
      }
    ]
  }
};