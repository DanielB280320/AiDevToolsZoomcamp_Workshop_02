"""Reference data for the mock database, mirroring frontend/src/api/mock/fixtures.js.

Clubs and logos are real; squads and results are generated from these seeds in generate.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Club:
    name: str
    code: str
    color: str
    name_pool: str
    logo: str


@dataclass(frozen=True)
class LeagueFixture:
    id: str
    name: str
    country: str
    region: str
    code: str
    logo: str
    season: str
    color: str
    double_round_robin: bool
    rounds_played: int
    club_ids: tuple[str, ...]  # roughly strongest-first; generate.py uses the order as team strength
    logo_background: str = "#ffffff"


NAME_POOLS = {
    "en": {
        "first": ["James", "Jack", "Harry", "Oliver", "George", "Callum", "Mason", "Declan", "Jordan", "Ben", "Kyle", "Reece", "Marcus", "Tyrone", "Lewis"],
        "last": ["Walker", "Taylor", "Hughes", "Mitchell", "Clarke", "Barnes", "Wright", "Porter", "Bennett", "Shaw", "Cole", "Fletcher", "Hayes", "Dawson", "Marsh"],
    },
    "es": {
        "first": ["Pablo", "Álvaro", "Sergio", "Dani", "Javi", "Marcos", "Iker", "Pedro", "Rodrigo", "Mikel", "Unai", "Hugo", "Adrián", "Raúl", "Fermín"],
        "last": ["García", "Fernández", "Martínez", "López", "Sánchez", "Romero", "Navarro", "Torres", "Ruiz", "Morales", "Ortega", "Castillo", "Vidal", "Herrera", "Molina"],
    },
    "it": {
        "first": ["Lorenzo", "Federico", "Alessandro", "Matteo", "Nicolò", "Davide", "Gianluca", "Andrea", "Riccardo", "Simone", "Marco", "Giacomo", "Luca", "Samuele", "Daniele"],
        "last": ["Rossi", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Esposito", "Mancini", "Costa", "Ferrara"],
    },
    "de": {
        "first": ["Lukas", "Leon", "Jonas", "Florian", "Niklas", "Maximilian", "Kai", "Julian", "Timo", "Felix", "Jannik", "Moritz", "Tobias", "Joshua", "Robin"],
        "last": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Wagner", "Becker", "Hoffmann", "Koch", "Richter", "Klein", "Wolf", "Braun", "Schäfer", "Krüger"],
    },
    "fr": {
        "first": ["Lucas", "Hugo", "Théo", "Jules", "Mathis", "Nathan", "Enzo", "Louis", "Rayan", "Adrien", "Maxime", "Yanis", "Bastien", "Clément", "Axel"],
        "last": ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Fontaine"],
    },
    "pt": {
        "first": ["Gabriel", "Lucas", "Pedro", "Matheus", "Bruno", "Rafael", "Vitor", "Thiago", "Everton", "Arthur", "Gustavo", "Léo", "Danilo", "João", "Caio"],
        "last": ["Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa", "Rodrigues", "Almeida", "Nascimento", "Lima", "Araújo", "Barbosa", "Ribeiro", "Carvalho", "Gomes"],
    },
    "latam": {
        "first": ["Santiago", "Julián", "Matías", "Diego", "Nicolás", "Emiliano", "Tomás", "Franco", "Alexis", "Rodrigo", "Enzo", "Joaquín", "Luis", "Raúl", "César"],
        "last": ["González", "Rodríguez", "Fernández", "Álvarez", "Gómez", "Díaz", "Pérez", "Romero", "Acosta", "Medina", "Herrera", "Aguirre", "Ramírez", "Flores", "Vega"],
    },
    "us": {
        "first": ["Tyler", "Brandon", "Christian", "Weston", "Josh", "Ethan", "Chris", "Sean", "Ricardo", "Diego", "Cade", "Miles", "Aidan", "Jordan", "Caleb"],
        "last": ["Adams", "Robinson", "Johnson", "Brooks", "Morgan", "Ferreira", "Carter", "Turner", "Miller", "Davis", "Long", "Parker", "Reed", "Bailey", "Hayes"],
    },
}

# (id, name, crest code, primary colour, name pool, logo URL)
_CLUB_ROWS = [
    ("liverpool", "Liverpool", "LIV", "#C8102E", "en", "https://r2.thesportsdb.com/images/media/team/badge/kfaher1737969724.png/small"),
    ("arsenal", "Arsenal", "ARS", "#EF0107", "en", "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png/small"),
    ("manchester-city", "Manchester City", "MCI", "#6CABDD", "en", "https://r2.thesportsdb.com/images/media/team/badge/vwpvry1467462651.png/small"),
    ("chelsea", "Chelsea", "CHE", "#034694", "en", "https://r2.thesportsdb.com/images/media/team/badge/pbf4ul1782638263.png/small"),
    ("newcastle-united", "Newcastle United", "NEW", "#241F20", "en", "https://r2.thesportsdb.com/images/media/team/badge/lhwuiz1621593302.png/small"),
    ("aston-villa", "Aston Villa", "AVL", "#670E36", "en", "https://r2.thesportsdb.com/images/media/team/badge/uwzw561787679026.png/small"),
    ("tottenham-hotspur", "Tottenham Hotspur", "TOT", "#132257", "en", "https://r2.thesportsdb.com/images/media/team/badge/dfyfhl1604094109.png/small"),
    ("manchester-united", "Manchester United", "MUN", "#DA291C", "en", "https://r2.thesportsdb.com/images/media/team/badge/xzqdr11517660252.png/small"),
    ("brighton", "Brighton & Hove Albion", "BHA", "#0057B8", "en", "https://r2.thesportsdb.com/images/media/team/badge/ywypts1448810904.png/small"),
    ("nottingham-forest", "Nottingham Forest", "NFO", "#DD0000", "en", "https://media.api-sports.io/football/teams/65.png"),

    ("barcelona", "Barcelona", "BAR", "#A50044", "es", "https://r2.thesportsdb.com/images/media/team/badge/wq9sir1639406443.png/small"),
    ("real-madrid", "Real Madrid", "RMA", "#FEBE10", "es", "https://r2.thesportsdb.com/images/media/team/badge/vwvwrw1473502969.png/small"),
    ("atletico-madrid", "Atlético Madrid", "ATM", "#CB3524", "es", "https://r2.thesportsdb.com/images/media/team/badge/0ulh3q1719984315.png/small"),
    ("athletic-club", "Athletic Club", "ATH", "#EE2523", "es", "https://r2.thesportsdb.com/images/media/team/badge/68w7fe1639408210.png/small"),
    ("villarreal", "Villarreal", "VIL", "#FFE667", "es", "https://r2.thesportsdb.com/images/media/team/badge/vrypqy1473503073.png/small"),
    ("real-betis", "Real Betis", "BET", "#00954C", "es", "https://r2.thesportsdb.com/images/media/team/badge/2oqulv1663245386.png/small"),
    ("real-sociedad", "Real Sociedad", "RSO", "#0067B1", "es", "https://r2.thesportsdb.com/images/media/team/badge/vptvpr1473502986.png/small"),
    ("celta-vigo", "Celta Vigo", "CEL", "#8AC3EE", "es", "https://r2.thesportsdb.com/images/media/team/badge/xfjtku1690436219.png/small"),
    ("sevilla", "Sevilla", "SEV", "#D71920", "es", "https://r2.thesportsdb.com/images/media/team/badge/vpsqqx1473502977.png/small"),
    ("valencia", "Valencia", "VAL", "#F18E00", "es", "https://r2.thesportsdb.com/images/media/team/badge/dm8l6o1655594864.png/small"),

    ("napoli", "Napoli", "NAP", "#12A0D7", "it", "https://r2.thesportsdb.com/images/media/team/badge/l8qyxv1742982541.png/small"),
    ("inter", "Inter", "INT", "#010E80", "it", "https://r2.thesportsdb.com/images/media/team/badge/ryhu6d1617113103.png/small"),
    ("atalanta", "Atalanta", "ATA", "#1E71B8", "it", "https://r2.thesportsdb.com/images/media/team/badge/qix5ku1780561327.png/small"),
    ("juventus", "Juventus", "JUV", "#1A1A1A", "it", "https://r2.thesportsdb.com/images/media/team/badge/uxf0gr1742983727.png/small"),
    ("roma", "Roma", "ROM", "#8E1F2F", "it", "https://r2.thesportsdb.com/images/media/team/badge/jwro2s1760820674.png/small"),
    ("milan", "Milan", "MIL", "#FB090B", "it", "https://r2.thesportsdb.com/images/media/team/badge/wvspur1448806617.png/small"),
    ("lazio", "Lazio", "LAZ", "#87D8F7", "it", "https://r2.thesportsdb.com/images/media/team/badge/rwqyvs1448806608.png/small"),
    ("bologna", "Bologna", "BOL", "#1A2F48", "it", "https://r2.thesportsdb.com/images/media/team/badge/2qi1u31655592366.png/small"),
    ("fiorentina", "Fiorentina", "FIO", "#482E92", "it", "https://r2.thesportsdb.com/images/media/team/badge/hc8nhu1656098030.png/small"),
    ("como", "Como", "COM", "#1B4A8F", "it", "https://r2.thesportsdb.com/images/media/team/badge/02x81t1627405841.png/small"),

    ("bayern-munich", "Bayern Munich", "FCB", "#DC052D", "de", "https://r2.thesportsdb.com/images/media/team/badge/01ogkh1716960412.png/small"),
    ("bayer-leverkusen", "Bayer Leverkusen", "B04", "#E32221", "de", "https://r2.thesportsdb.com/images/media/team/badge/3x9k851726760113.png/small"),
    ("eintracht-frankfurt", "Eintracht Frankfurt", "SGE", "#1A1A1A", "de", "https://r2.thesportsdb.com/images/media/team/badge/rurwpy1473453269.png/small"),
    ("borussia-dortmund", "Borussia Dortmund", "BVB", "#FDE100", "de", "https://r2.thesportsdb.com/images/media/team/badge/tqo8ge1716960353.png/small"),
    ("sc-freiburg", "SC Freiburg", "SCF", "#D5001C", "de", "https://r2.thesportsdb.com/images/media/team/badge/urwtup1473453288.png/small"),
    ("mainz-05", "Mainz 05", "M05", "#C3141E", "de", "https://r2.thesportsdb.com/images/media/team/badge/fhm9v51552134916.png/small"),
    ("rb-leipzig", "RB Leipzig", "RBL", "#0C2043", "de", "https://r2.thesportsdb.com/images/media/team/badge/zjgapo1594244951.png/small"),
    ("werder-bremen", "Werder Bremen", "SVW", "#1D9053", "de", "https://r2.thesportsdb.com/images/media/team/badge/tkvqan1716960454.png/small"),
    ("vfb-stuttgart", "VfB Stuttgart", "VFB", "#E32219", "de", "https://r2.thesportsdb.com/images/media/team/badge/yppyux1473454085.png/small"),
    ("borussia-monchengladbach", "Borussia Mönchengladbach", "BMG", "#2B2B2B", "de", "https://r2.thesportsdb.com/images/media/team/badge/sysurw1473453380.png/small"),

    ("flamengo", "Flamengo", "FLA", "#C52613", "pt", "https://r2.thesportsdb.com/images/media/team/badge/syptwx1473538074.png/small"),
    ("palmeiras", "Palmeiras", "PAL", "#006437", "pt", "https://r2.thesportsdb.com/images/media/team/badge/vsqwqp1473538105.png/small"),
    ("cruzeiro", "Cruzeiro", "CRU", "#2F529E", "pt", "https://r2.thesportsdb.com/images/media/team/badge/upsvvu1473538059.png/small"),
    ("botafogo", "Botafogo", "BOT", "#1A1A1A", "pt", "https://r2.thesportsdb.com/images/media/team/badge/bs5mbw1733004596.png/small"),
    ("fluminense", "Fluminense", "FLU", "#870A28", "pt", "https://r2.thesportsdb.com/images/media/team/badge/stvvwp1473538082.png/small"),
    ("sao-paulo", "São Paulo", "SAO", "#FE0000", "pt", "https://r2.thesportsdb.com/images/media/team/badge/sxpupx1473538135.png/small"),
    ("internacional", "Internacional", "SCI", "#E5050F", "pt", "https://r2.thesportsdb.com/images/media/team/badge/yprvxx1473538097.png/small"),
    ("corinthians", "Corinthians", "COR", "#2B2B2B", "pt", "https://r2.thesportsdb.com/images/media/team/badge/vvuvps1473538042.png/small"),
    ("atletico-mineiro", "Atlético Mineiro", "CAM", "#3A3A3A", "pt", "https://r2.thesportsdb.com/images/media/team/badge/x5lixs1743742872.png/small"),
    ("gremio", "Grêmio", "GRE", "#0D80BF", "pt", "https://r2.thesportsdb.com/images/media/team/badge/uvpwyt1473538089.png/small"),

    ("toluca", "Toluca", "TOL", "#D6001C", "latam", "https://r2.thesportsdb.com/images/media/team/badge/y64wy91523913186.png/small"),
    ("club-america", "Club América", "AME", "#FFD700", "latam", "https://r2.thesportsdb.com/images/media/team/badge/amy1xs1581857392.png/small"),
    ("cruz-azul", "Cruz Azul", "CAZ", "#003DA5", "latam", "https://r2.thesportsdb.com/images/media/team/badge/wcd2yi1781543370.png/small"),
    ("tigres-uanl", "Tigres UANL", "TIG", "#FDB913", "latam", "https://media.api-sports.io/football/teams/2279.png"),
    ("monterrey", "Monterrey", "MTY", "#002B5C", "latam", "https://r2.thesportsdb.com/images/media/team/badge/yglj911721542561.png/small"),
    ("pachuca", "Pachuca", "PAC", "#004B8D", "latam", "https://r2.thesportsdb.com/images/media/team/badge/k9duyw1747334895.png/small"),
    ("guadalajara", "Guadalajara", "GDL", "#CD1F2D", "latam", "https://r2.thesportsdb.com/images/media/team/badge/mp1box1593452087.png/small"),
    ("pumas-unam", "Pumas UNAM", "PUM", "#B08D57", "latam", "https://media.api-sports.io/football/teams/2286.png"),
    ("tijuana", "Tijuana", "TIJ", "#C8102E", "latam", "https://r2.thesportsdb.com/images/media/team/badge/b0mky81779772352.png/small"),
    ("leon", "León", "LEO", "#006341", "latam", "https://r2.thesportsdb.com/images/media/team/badge/pc9gro1752393439.png/small"),

    ("inter-miami", "Inter Miami", "MIA", "#F7B5CD", "us", "https://r2.thesportsdb.com/images/media/team/badge/m4it3e1602103647.png/small"),
    ("la-galaxy", "LA Galaxy", "LAG", "#00245D", "us", "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png/small"),
    ("columbus-crew", "Columbus Crew", "CLB", "#FEDD00", "us", "https://r2.thesportsdb.com/images/media/team/badge/dzs8cp1629059854.png/small"),
    ("fc-cincinnati", "FC Cincinnati", "CIN", "#F05323", "us", "https://r2.thesportsdb.com/images/media/team/badge/vvhsqc1707631046.png/small"),
    ("lafc", "LAFC", "LAFC", "#C39E6D", "us", "https://r2.thesportsdb.com/images/media/team/badge/7nbj2a1602103638.png/small"),
    ("seattle-sounders", "Seattle Sounders", "SEA", "#5D9741", "us", "https://r2.thesportsdb.com/images/media/team/badge/2dy5cx1706711036.png/small"),
    ("philadelphia-union", "Philadelphia Union", "PHI", "#071B2C", "us", "https://r2.thesportsdb.com/images/media/team/badge/gyznyo1602103682.png/small"),
    ("orlando-city", "Orlando City", "ORL", "#633492", "us", "https://r2.thesportsdb.com/images/media/team/badge/qyppxw1423832326.png/small"),
    ("vancouver-whitecaps", "Vancouver Whitecaps", "VAN", "#9DC2EA", "us", "https://r2.thesportsdb.com/images/media/team/badge/tpwxpy1473536521.png/small"),
    ("new-york-city-fc", "New York City FC", "NYC", "#6CACE4", "us", "https://r2.thesportsdb.com/images/media/team/badge/m9vis71735140655.png/small"),

    ("river-plate", "River Plate", "RIV", "#EB192E", "latam", "https://r2.thesportsdb.com/images/media/team/badge/03dmi31645539717.png/small"),
    ("boca-juniors", "Boca Juniors", "BOC", "#103F79", "latam", "https://r2.thesportsdb.com/images/media/team/badge/bm7krb1775741582.png/small"),
    ("racing-club", "Racing Club", "RAC", "#6CACE4", "latam", "https://r2.thesportsdb.com/images/media/team/badge/vi4mu41695734959.png/small"),
    ("independiente", "Independiente", "IND", "#E30613", "latam", "https://r2.thesportsdb.com/images/media/team/badge/eki4nd1580842605.png/small"),
    ("velez-sarsfield", "Vélez Sarsfield", "VEL", "#0B3B8C", "latam", "https://r2.thesportsdb.com/images/media/team/badge/jo98m71517769587.png/small"),
    ("estudiantes", "Estudiantes", "EST", "#E4002B", "latam", "https://media.api-sports.io/football/teams/450.png"),
    ("talleres", "Talleres", "TAL", "#002E6D", "latam", "https://r2.thesportsdb.com/images/media/team/badge/7hum2t1769310938.png/small"),
    ("san-lorenzo", "San Lorenzo", "SLO", "#0B2A5B", "latam", "https://media.api-sports.io/football/teams/460.png"),
    ("rosario-central", "Rosario Central", "CEN", "#0033A0", "latam", "https://r2.thesportsdb.com/images/media/team/badge/y6q1ds1769660256.png/small"),
    ("huracan", "Huracán", "HUR", "#E30613", "latam", "https://r2.thesportsdb.com/images/media/team/badge/kppi2b1775776550.png/small"),

    ("paris-saint-germain", "Paris Saint-Germain", "PSG", "#004170", "fr", "https://media.api-sports.io/football/teams/85.png"),
]

CLUBS = {club_id: Club(name, code, color, pool, logo) for club_id, name, code, color, pool, logo in _CLUB_ROWS}

LEAGUES = [
    LeagueFixture(
        id="premier-league", name="Premier League", country="England", region="Europe", code="ENG",
        logo="https://r2.thesportsdb.com/images/media/league/badge/gasy9d1737743125.png/small",
        season="2026–27", color="#3D1159", double_round_robin=True, rounds_played=12,
        club_ids=("liverpool", "arsenal", "manchester-city", "chelsea", "newcastle-united", "aston-villa", "tottenham-hotspur", "manchester-united", "brighton", "nottingham-forest"),
    ),
    LeagueFixture(
        id="la-liga", name="La Liga", country="Spain", region="Europe", code="ESP",
        logo="https://r2.thesportsdb.com/images/media/league/badge/ja4it51687628717.png/small",
        season="2026–27", color="#D6312B", double_round_robin=True, rounds_played=12,
        club_ids=("barcelona", "real-madrid", "atletico-madrid", "athletic-club", "villarreal", "real-betis", "real-sociedad", "celta-vigo", "sevilla", "valencia"),
    ),
    LeagueFixture(
        id="serie-a", name="Serie A", country="Italy", region="Europe", code="ITA",
        logo="https://r2.thesportsdb.com/images/media/league/badge/67q3q21679951383.png/small",
        season="2026–27", color="#1B4FA0", double_round_robin=True, rounds_played=12,
        club_ids=("napoli", "inter", "atalanta", "juventus", "roma", "milan", "lazio", "bologna", "fiorentina", "como"),
    ),
    LeagueFixture(
        id="bundesliga", name="Bundesliga", country="Germany", region="Europe", code="GER",
        logo="https://r2.thesportsdb.com/images/media/league/badge/teqh1b1679952008.png/small",
        season="2026–27", color="#C8102E", double_round_robin=True, rounds_played=12,
        club_ids=("bayern-munich", "bayer-leverkusen", "eintracht-frankfurt", "borussia-dortmund", "sc-freiburg", "mainz-05", "rb-leipzig", "werder-bremen", "vfb-stuttgart", "borussia-monchengladbach"),
    ),
    LeagueFixture(
        id="brasileirao", name="Brasileirão Série A", country="Brazil", region="Americas", code="BRA",
        logo="https://r2.thesportsdb.com/images/media/league/badge/lywv7t1766787179.png/small",
        season="2026", color="#00843D", double_round_robin=True, rounds_played=12,
        club_ids=("flamengo", "palmeiras", "cruzeiro", "botafogo", "fluminense", "sao-paulo", "internacional", "corinthians", "atletico-mineiro", "gremio"),
    ),
    LeagueFixture(
        id="liga-mx", name="Liga MX", country="Mexico", region="Americas", code="MEX",
        logo="https://r2.thesportsdb.com/images/media/league/badge/mav5rx1686157960.png/small",
        season="2026–27", color="#0B6E4F", double_round_robin=True, rounds_played=12,
        club_ids=("toluca", "club-america", "cruz-azul", "tigres-uanl", "monterrey", "pachuca", "guadalajara", "pumas-unam", "tijuana", "leon"),
    ),
    LeagueFixture(
        id="mls", name="MLS", country="USA / Canada", region="Americas", code="USA",
        logo="https://r2.thesportsdb.com/images/media/league/badge/dqo6r91549878326.png/small",
        season="2026", color="#1B2F5E", double_round_robin=True, rounds_played=12,
        club_ids=("inter-miami", "la-galaxy", "columbus-crew", "fc-cincinnati", "lafc", "seattle-sounders", "philadelphia-union", "orlando-city", "vancouver-whitecaps", "new-york-city-fc"),
    ),
    LeagueFixture(
        id="primera-division", name="Primera División", country="Argentina", region="Americas", code="ARG",
        logo="https://r2.thesportsdb.com/images/media/league/badge/rk9xhx1768238251.png/small",
        season="2026", color="#2A6FB0", double_round_robin=True, rounds_played=12,
        club_ids=("river-plate", "boca-juniors", "racing-club", "independiente", "velez-sarsfield", "estudiantes", "talleres", "san-lorenzo", "rosario-central", "huracan"),
    ),
    LeagueFixture(
        id="champions-league", name="UEFA Champions League", country="Europe", region="Continental", code="UCL",
        logo="https://r2.thesportsdb.com/images/media/league/badge/facv1u1742998896.png/small",
        season="2026–27", color="#0B1F63", logo_background="#0B1F63", double_round_robin=False, rounds_played=8,
        club_ids=("real-madrid", "bayern-munich", "liverpool", "arsenal", "barcelona", "inter", "paris-saint-germain", "manchester-city", "atletico-madrid", "borussia-dortmund"),
    ),
]
