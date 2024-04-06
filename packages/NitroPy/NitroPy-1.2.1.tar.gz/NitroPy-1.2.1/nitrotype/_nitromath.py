import cloudscraper
from bs4 import BeautifulSoup
import json
import re
import asyncio


__all__ = [
    "NitromathRacer"
]


#cars of nitromath
cars = {
    1 : 'Lamborgotti Mephisto SS',
    2 : 'Lamborgotti Mephisto',
    3 : 'Jeepers Rubicorn',
    4 : 'Portch Picante',
    5 : 'Bantly Super Sport',
    6 : 'The Rolls',
    7 : 'Winston Citroen',
    8 : 'Winston Agile',
    9 : 'Rental Car',
    10 : 'Mission Accomplished',
    11 : 'Buggani Vyrus SS',
    13 : 'Auttie B9',
    14 : 'Nitsua Lance 722',
    15 : 'Misoux Lion',
    16 : 'Misoux Toad',
    17 : 'Minnie the Cooper',
    18 : 'Nizza 350x',
    19 : 'One Ace',
    20 : 'Cougar Ace',
    21 : 'Rand Rover R/T',
    22 : 'B-Team Van',
    23 : 'Mercedex Bens V-20',
    24 : 'Mercedex Bens C-64',
    25 : 'Portch Spyder',
    26 : 'Auttie Roadster',
    27 : 'Bimmer M2.0',
    28 : 'Bimmer 9.0t',
    29 : 'Thunder Cougarbird',
    30 : 'Rat Rod Skully',
    31 : 'Outtie R11',
    33 : 'The Flamerod',
    34 : 'Valent Performo',
    35 : 'Portch GT3 RS',
    36 : 'Ponce de Leon',
    37 : '\'67 Shellback GT-500',
    38 : 'Road Warrior',
    39 : 'Linux Elise',
    40 : '\'69 Shellback RT-500',
    42 : 'The Gator',
    43 : 'Bastok Suprillia',
    44 : 'The Judge',
    45 : 'The Stallion',
    46 : 'The Macro',
    47 : 'The Fastback',
    48 : 'The Covenant',
    49 : 'The Trifecta',
    50 : '8 Bit Racer',
    51 : 'Mini Sherman',
    52 : 'Typiano Pizza Car',
    53 : 'Rocket Man',
    54 : 'All Terrain Vehicle',
    55 : 'MP 427',
    56 : 'Wambulance',
    57 : 'Hotdog Mobile',
    58 : 'F-35 JSF',
    59 : 'NASA Shuttle',
    60 : 'Caterham Racer',
    61 : 'Mack Daddy',
    62 : 'Big Hauler',
    63 : 'Big Blue  ',
    64 : 'Fort GT40',
    65 : 'Dom Vipper GST-R',
    66 : 'Alpha Romero 8Ω',
    67 : 'Blazing Buggy',
    68 : 'F4U Corsair',
    69 : 'Rocket Sleigh',
    70 : 'XMaxx Tree Racer',
    71 : 'Shadow Xmaxx Tree',
    72 : 'Party Sleigh',
    73 : 'Zonday Tricolore',
    74 : 'The Monster',
    75 : 'Flux Capacitor',
    76 : 'The Gotham',
    77 : 'The Pirc',
    78 : 'Suziki GXRS 1200',
    79 : 'EZ Rider',
    80 : 'Lamborgotti AdventX',
    81 : 'Summer Classic',
    82 : 'Hang Ten',
    83 : '\'41 Woodie Deluxx',
    84 : 'Hang Eleven',
    85 : '\'41 Woodie Sunshine',
    86 : 'The Xcelsior V12',
    87 : '\'68 Roadtripper',
    88 : 'Hang Fifteen',
    89 : 'Wach 6',
    90 : 'Fort F-125',
    91 : 'Wisker Electric',
    92 : '\'67 Vette',
    93 : 'MSG 01',
    94 : 'Fort Stallion',
    95 : 'Police Bimmer',
    96 : 'Auttie R-8.1',
    97 : 'Wampus',
    98 : 'Pumpkin Hauler',
    99 : 'Wreath Racer',
    100 : 'Santa\'s Buggy',
    101 : 'Travis\' Car',
    102 : 'Dark Elf',
    103 : 'The Golden Gift',
    104 : 'Corndog\'s Car',
    105 : '\'14 Mantaray',
    106 : 'Ferreti Samsher 458',
    107 : 'Lacan Hypersport',
    109 : 'Sun Buggie',
    110 : 'Hammer Wheels',
    111 : 'Kringle 4000',
    112 : 'Buddy\'s Snowmobile',
    113 : 'Kringle 4000 XL',
    114 : 'Buddy\'s Snowmorocket',
    115 : 'Six Four',
    116 : 'Six Four Plus Three',
    117 : 'The Midnight Hauler',
    118 : 'The Candy Hauler',
    119 : 'Kringle 5000',
    120 : 'Wrapped Wracer',
    121 : 'Wrapped Wracer GT',
    122 : 'Holiday Hero',
    123 : 'Kringle 5000 L.T.',
    124 : 'Mercedex McLaro SLR',
    125 : 'Floaty Blue',
    126 : 'B.O.A.T.',
    127 : 'I\'m Spicy!',
    128 : 'Y.A.C.H.T.',
    129 : 'Mercedex McLaro SLR 12.5',
    130 : 'Nitr-o\'-Lantern',
    131 : 'Nitr-o\'-the-Wisp',
    132 : 'Xmaxx Xxpress',
    133 : 'XMaxx Xxpress XXL',
    134 : 'Gilded Xxpress',
    135 : 'Lamborgotti Xmaxx LT',
    136 : 'Lamborgotti Xmaxx LT-C',
    137 : 'Mercedex McLaro SHS 15.0',
    138 : 'Strykist 1300',
    139 : 'Range Runner',
    140 : 'Strykist 1300 XT-LR',
    141 : 'Track-o\'-Lantern',
    142 : 'Gingerbread Racer',
    143 : 'Gingerbread Racer H&T',
    144 : 'Missile Toe',
    145 : 'Missile Toe H&T',
    146 : 'The Dark Chocolate Knight',
    149 : 'Teggsla',
    150 : 'Egg Beater',
    151 : 'Eggcedes',
    152 : 'Egg Hauler',
    153 : 'Mercedex GT 20.0',
    154 : 'Rocky Roo',
    155 : 'NitroPAC',
    156 : 'Matchbox',
    157 : 'Lucky Number 7',
    158 : 'Easy Breezy',
    159 : 'HoverJet 5000 Mk. 3',
    160 : 'Golden Breeze',
    161 : 'B.U.S.',
    162 : 'S\'cool B.U.S.',
    163 : 'AU-79',
    164 : 'The Underachiever',
    165 : 'The Overachiever',
    166 : 'The Wildflower',
    167 : 'Jolly RS',
    168 : 'Jolly GTX LG',
    169 : 'The Goldray',
    170 : 'can hav nt g0ld plx?',
    171 : 'The Wraptor',
    172 : 'Travis\' Truck',
    173 : 'The Wraptor GG',
    174 : 'The Silent Knight',
    175 : 'NT Gold',
    176 : 'Lamborgotti Tiesto',
    177 : 'Portch Cobalt',
    178 : 'Alpha Romero 123Ω',
    179 : 'Travis\' Big Truck',
    180 : 'Bright Idea',
    181 : 'Sandstorm',
    182 : 'The Jury',
    183 : 'The Goldfish',
    184 : 'Shock Value',
    185 : 'Gold Standard',
    186 : 'Solar Roller',
    187 : 'H2GO',
    188 : 'The DevasTater',
    189 : 'Creepy Crawler',
    190 : 'The Goblin',
    191 : 'Something Wicked',
    192 : 'Frosted Roller',
    193 : 'Gingerbread GT',
    194 : 'Holiday Heat',
    195 : 'Cold Snap',
    196 : 'The Snowy Knight',
    197 : 'The Rocket Klaus',
    198 : 'Golden Ticket',
    199 : 'Wavebreaker',
    200 : 'Broadwing',
    201 : 'Bimmer Prism i20',
    202 : 'Heartbreaker',
    203 : 'The Danger 9',
    204 : 'The Wild 500',
    205 : 'Tigreen',
    206 : 'X1 Eclipse',
    207 : 'Error 500',
    208 : 'Vapor',
    209 : '9 Bit Racer',
    210 : 'Chompus\' Wild Ride',
    211 : 'Whiplash XS',
    212 : 'The Hydro Planer',
    213 : 'Timber Speeder',
    214 : 'Wampus\' Waffle Wagon',
    215 : 'Webmobile Spider',
    216 : 'Rand Rover Evar',
    217 : 'SpaceZ Crew Draco',
    218 : 'MacLaro Sienna',
    219 : 'Calculatron',
    220 : 'Screw Tank',
    221 : 'Hoverbike',
    222 : 'Jet Bicycle',
    223 : 'Wrapped Flyer',
    224 : 'The Festivitank',
    227 : 'Maxxbilt Jetro',
    228 : 'Corsa Vengeance',
    230 : 'X2 Eclipse',
    232 : 'Liberty Redux',
    233 : 'Liberty Leo', 
    234 : 'Fonicci Tricolore 2021',
    235 : 'Winson Gator Ayd',
    236 : 'Liberty Glamrod',
    237 : 'Winson Linux',
    238 : 'Liberty Warrior NRX',
    239 : 'Furious Maxx', 
    241 : 'Blitz M6',
    242 : 'The Dominator',
    243 : 'Flux Heartbreaker LV-2',
    244 : 'Maxxbilt Ice Hauler',
    245 : 'The Kelvin',
    246 : 'Nitreux Vyrus LR',
    247 : 'Corsa Error 503',
    249 : 'Shimura Sprinter \'90',
    250 : 'Koromoto NRX',
    251 : 'Flux M400-R',
    252 : 'Koromoto DJ Cruiser',
    253 : 'Koromoto GT-R',
	254 : 'Koromoto GT-R LS',
	255 : 'Stingtec Technotruck',
	256 : 'Four Leaf Rover',
	257 : 'Corsa Iris',
	258 : 'Sprinter \'90 Vapor',
	259 : 'Winson Track\'d',
	260 : 'Corsa Mystica',
	261 : 'Stingtec Marianas',
	262 : 'Stingtec WaterSki',
	263 : 'Blitz T8 Roadster',
	264 : 'Liberty Demon XRT',
	265 : 'Koromoto GT-R Neon',
	266 : 'Mongoose SU-5',
	267 : 'Corsa Megalodor',
	268 : 'The Evergreen Steamer',
	269 : 'Bozz Juice\'d',
	270 : 'Stingtec Thunderboat',
	271 : 'Blitz Dune Bounder',
	272 : 'Corsa Contacc',
	273 : 'Liberty Rescue',
	274 : 'Hydrova OG',
	276 : 'Flux Memo',
	277 : 'Fully Leaded',
	278 : 'Konirra Celebrar EVO',
	279 : 'Koromoto Rulebreaker',
	280 : 'S’cool B.U.S. Wildn',
	281 : 'Evergreen Screamer',
	282 : 'Ghoul Bus',
	283 : 'Blitz 935 Sunset',
	284 : 'Cartrod',
	285 : 'Hay, a Truck',
	286 : 'Harvestall Tractor',
	287 : 'Liberty S7',
	288 : 'T. Butler #56',
	289 : 'A. Butler #12',
	290 : 'Bobby Ricky #3',
	291 : 'K. Smith #23',
	292 : 'H. Bonacci #8',
	293 : 'K. Osburn #21',
	294 : 'Mini Firetruck',
	295 : 'Graffiti Tank',
	297 : 'Elfmobile \'21',
	298 : 'Fonicci Candido F8',
	299 : 'Party Sleigh Neon',
	300 : 'Lit Locomotive',
	301 : 'Snowcat Luxe',
	302 : 'LED Streetracer',
	303 : 'Nada Racer',
	304 : 'Blitz Esperante',
	305 : 'Heart-Shaped Car',
	306 : 'Fonicci Zucchero',
	307 : 'Ice Cream Truck',
	308 : 'Bozz Advent',
	309 : 'Hydrova Razorback',
	310 : 'Stingtec x427 Super',
	311 : 'Randon 620',
	312 : 'Stingtec Manta',
	313 : 'The Wildflower 750',
	314 : 'Sour Truck',
	315 : 'Corsa Tiesto "ColdSnap"',
	316 : 'Liberty Shellback "Firestorm"',
	317 : 'Koromoto GT-R "Tempest"',
	318 : 'AU-79 Mk. 18',
	319 : 'Winson Velox',
	320 : 'Stingtec DL-XT',
	321 : 'Liberty Model H',
	322 : 'Stingtec Wells GT',
	323 : 'S.H.I.P.',
	324 : 'Nitreux Zephyrus',
	325 : 'Liberty \'81 Chief ST',
	326 : 'The Nitro Machine',
	327 : 'Typiano Delivery Van',
	328 : 'Boatie Classic',
	329 : 'Flux XR Sport',
	330 : 'Fonicci Rego',
	331 : 'Nitreux F1',
	332 : 'Blitz Tetra S1',
	333 : 'Liberty YT-5K',
	334 : 'Blitz Slipstream',
	335 : 'FestiveZep',
	336 : 'Maxx\'d-Out Shadow Tree',
	337 : 'Corsa Festivi-X',
	338 : 'The Winter Wonder',
	339 : 'Frostbite XT',
	340 : 'Nitreux Azune',
	341 : 'Zon Bike',
	342 : 'RMS Unsinkable',
	343 : 'Mach 3 Marvel',
	344 : 'Boogeyman Buster',
	345 : 'Nitreux Vielleux',
	346 : 'Mach 10 Maverick',
	347 : 'Fonicci Equinox',
	348 : 'Winson Maythaw',
	349 : 'Koromoto Cerberus',
	350 : 'Viper Vortex',
	351 : 'Swamp Speedster',
	352 : 'Feline Fury',
	353 : 'Expedition Explorer',
	354 : 'Avian Aero',
	355 : 'Blitz Excalibur GT',
	356 : 'Blitz Nebula',
	357 : 'Konirra Apex',
	359 : 'Stingtec F1',
	360 : 'Fonicci Aegis',
	361 : 'Gotham Guardian',
	362 : 'Fonicci Hyperion SS',
    367 : 'Nitreux Quantum',
    368 : 'Choppa'
}

class NitromathRacer:
    def __init__(self, username):
        self.username = username
        self._scraper = cloudscraper.create_scraper()
        self._racer_info = self._get_user_info()
        self._initialize_attributes()

    def _get_user_info(self):
        response = self._scraper.get(f'https://www.nitromath.com/racer/{self.username}').text
        soup = BeautifulSoup(response, 'html.parser')

        racer_info = {}
        for script in soup.find_all('script'):
            if 'RACER_INFO' in str(script):
                racer_info = json.loads(re.findall('{".+}', str(script))[0])
                return racer_info

        return None
    

    async def get_gold_data(self):
        resp = self._scraper.post('https://www.nitromath.com/api/v2/payments/products/', data={'username': self.username, 'type': 'gold'})
        purchases_response = json.loads(resp.text)

        if 'results' in purchases_response:
            results = purchases_response['results']
            if 'user' in results:
                user_data = results['user']
                expiration_date = user_data.get('goldUntil', 'None')
                last_purchase_date = user_data.get('lastPurchase', 'None')
                return expiration_date, last_purchase_date
        return 'None', 'None'
    
        

    def _initialize_attributes(self):
        # Initialize attributes
        racer_info = self._racer_info
        self.user_id = racer_info['userID']
        self.username = racer_info['username']
        self.membership = racer_info['membership']
        self.display_name = racer_info['displayName']
        self.title = racer_info['title']
        self.experience = racer_info['experience']
        self.level = racer_info['level']
        self.team_id = racer_info['teamID']
        self.looking_for_team = bool(racer_info['lookingForTeam'])
        self.car_id = racer_info['carID']
        self.car_hue_angle = racer_info['carHueAngle']
        self.total_cars = len(racer_info['garage'])
        self.nitros_total = racer_info['nitros']
        self.nitros_used = racer_info['nitrosUsed']
        self.games = racer_info['racesPlayed']
        self.longest_session = racer_info['longestSession']
        self.average_speed = racer_info['avgSpeed']
        self.highest_speed = racer_info['highestSpeed']
        self.friend_reqs_allowed = bool(racer_info['allowFriendRequests'])
        self.profile_views = racer_info['profileViews']
        self.created = racer_info['createdStamp']
        self.tag = racer_info['tag']
        self.tag_color = racer_info['tagColor']
        self.car_image = f"https://magmal-official.fly.dev/static/cars/{self.car_id}.png"

        # Fetch membership data
        loop = asyncio.get_event_loop()
        membership_expiration, membership_last_purchase = loop.run_until_complete(self.get_gold_data())
        self.membership_expiration = membership_expiration
        self.membership_last_purchase = membership_last_purchase

        nametag = next((loot for loot in racer_info.get('loot', []) if loot['type'] == 'nametag'), None)
        if nametag:
            self.nametag_name = nametag['name']
            self.nametag_id = nametag['lootID']
            self.nametag_rarity = nametag['options']['rarity']
            self.nametag_img = f"https://www.nitromath.com{nametag['options']['src']}"
        else:
            self.nametag_name = None
            self.nametag_id = None
            self.nametag_rarity = None
            self.nametag_img = None

        trail = next((loot for loot in racer_info.get('loot', []) if loot['type'] == 'trail'), None)
        if trail:
            self.trail_name = trail['name']
            self.trail_id = trail['lootID']
            self.trail_rarity = trail['options']['rarity']
            self.trail_img = f"https://www.nitromath.com{trail['options']['src']}"
        else:
            self.trail_name = None
            self.trail_id = None
            self.trail_rarity = None
            self.trail_img = None

    @property
    def current_car_name(self):
        return cars.get(self.car_id, "Unknown")


    def __getattr__(self, attr):
        if attr in self._racer_info:
            return self._racer_info[attr]
        raise AttributeError(f"'NitromathRacer' object has no attribute '{attr}'")