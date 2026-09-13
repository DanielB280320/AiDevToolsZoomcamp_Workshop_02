# Kickboard — Project Specification
### (Football League Scoreboard)
 
## 1. Overview
A web application that lets a user track standings across the world's most important football leagues, and drill into any team to see key performance details (top scorer, best player in the last match, squad, and recent results).
 
## 2. Leagues Covered
 
**Europe (4)**
- Premier League (England)
- La Liga (Spain)
- Serie A (Italy)
- Bundesliga (Germany)
**Americas (4)**
- Brasileirão / Brazil Série A
- Liga MX (Mexico)
- MLS (USA/Canada)
- Primera División (Argentina)
**Continental**
- UEFA Champions League
## 3. Standings Table (per league)
Each league's table shows, per team:
- Position
- Team name (+ crest)
- Games Played
- Wins / Draws / Losses
- Goal Difference
- Points

## 4. Team Detail View
Clicking into a team shows:
- **Top scorer** — player with most goals for that team this season
- **Best player in last match** — determined by a **composite score**: goals + assists + match rating + minutes played (weighted formula, tunable later)
- **Full squad list** — players grouped by position (GK / DEF / MID / FWD)
- **Recent match results** — last 5 games with score, opponent, W/D/L

## 5. Data Strategy
- **Phase 1 (now):** Mock/sample JSON data, structured to mirror what a real API would return.
- **Phase 2 (later):** Swap in a real sports data API (e.g. API-Football, SportRadar) without changing the frontend's data-consumption layer. All data-fetching should go through a single service/adapter module so this swap is low-friction.

## 6. Navigation & Layout
- **Sidebar:** lists all leagues (Europe, Americas, Champions League grouped)
- **Main area:** displays the standings table for the currently selected league
- Clicking a team row opens the team detail view (panel or dedicated route)

## 7. Visual Style
- Clean, minimal aesthetic — similar to official league websites
- Neutral base palette, with team crest colors used sparingly as accents
- Prioritize legibility of tabular data over decorative elements

## 8. Tech Stack
- **Frontend:** React
- **Data layer:** Local mock JSON files now, abstracted behind a data-service module for future API integration
- **Styling:** TBD at build time (e.g. Tailwind or CSS modules) — not fixed by this spec

## 9. Data Model (draft)
 
```
League
- id, name, country/region, logo
 
Team
- id, name, leagueId, crest, position, played, wins, draws, losses,
  goalDifference, points
 
Player
- id, teamId, name, position, goals, assists
 
Match
- id, leagueId, homeTeamId, awayTeamId, homeScore, awayScore, date
- playerRatings: [{ playerId, goals, assists, rating, minutesPlayed }]
```
 
## 10. Best Player Composite Score (draft formula)
```
score = (goals * 4) + (assists * 3) + (rating * 2) + (minutesPlayed / 90)
```
Weights are placeholders — tune once real match data is available.
 
## 11. Out of Scope (for now)
- Live/real-time score updates
- User accounts, favorites, or notifications
- Historical seasons / archives
- Betting odds or predictions

## 12. Next Steps
1. Build mock data fixtures for all 9 competitions
2. Build React app: sidebar + standings table + team detail view
3. Validate UX with mock data
4. Integrate real sports data API