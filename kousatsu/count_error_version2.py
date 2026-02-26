import json
import re
from ollama import Client
# -----------------------------
# keep list
# -----------------------------
# 0があったもの
# keep_base_names = ['mesh', 'rental-source', 'mailmaps-email-marketing', 'it-cookie-time', 'japan-talent-data-box', 'qabic', 'yappoint', 'gifanator', 'starbucks-digital-network', 'datantify', 'cheap-flights-to', 'us-virtual-neighborhood', 'cheap-flights-to-0', 'mapyou', 'booli.se', 'meetbymaps', 'boyfriend-x', 'enthusem-and-box.net', 'esync-dashboard', 'swine-flu-outbreak-dashboard', 'elementary-mail', 'social-interest', 'are-my-sites-white-label', 'locago', 'kolay-%C3%A4%C2%B0ngilizce-oku', 'street-art-map', 'mattfind.com', 'dvdcrate.com', 'lyricsgaps.com', 'emory-law-events', 'pick-your-perfect-pet', 'time-machine', 'your-automated-china-investment-advisor', 'backup-box', 'dinero.no', 'listmaniacc', 'realwebstats', 'geo-messages', 'usersthink', 'croctail-corporate-watch', 'json-api-app', 'seegest', 'printout-designer-20', 'ny-times-timesmachine', 'rock-climbing-mexico', 'onair-city-tracker', 'dog-pedigrees-online', 'gotime-iphone', 'finderface', 'deki-wiki', 'noms.', 'itrackmine.com', 'conner-outdoors', 'worldfactorium', 'ihear-network', 'morces', 'tallyspace', 'bild.de-desktop', 'world-movie-search', 'buoy-alarm', 'blocks-and-lots', 'vacationic', 'giphy-and-twilio-text-gif', 'venmo', 'moveable-weather', 'abouthisite', 'pdfcast', 'germtrax', 'best-hospitals-cancer-treatment', '99designs-tasks-slack-bot', 'localmouth', '200-towns', 'ok-travel-australia', 'make-me-change-my-job', 'tout', 'editgrid-and-box.net', 'infinilla', 'ditto', 'decisions-heroes-0', 'vgpedia.net', 'quickblox-ios-supersample', 'papership', 'datacalifornia', 'google-apps-and-box.net', 'ness-dining-guide', 'song.ly', 'feedbackfire', 'dbstract.com', 'ideum', 'us-top-business-schools-map', 'thetool', 'turtilla-rss-mashup-tool', 'fanbible', 'girlfriend-x', 'music-codex.com', 'day-one-app', 'best-dining', 'allmusic-rovi', 'crimelit', 'vehive.com', 'car-emissions-calculator', 'pulse-medic', 'learnit-lists', 'get-rhythm', 'crowdbeacon', 'analytics-edge-connector-moz', 'happy-hour-share', 'infobiliaria-spain', 'icecharge', 'contentful', 'motivation-mix', 'all-world-national-anthems-mashup-service']
# keep_base_names = ['mesh']
#普通のもの
keep_base_names=['slidemypics', 'snoopf', 'my-powers-out', 'moveboxer', 'myetsybook.com', 'demo-bookstore-amazon-advertising-api', 'yaptap', 'pushr', 'symbyoz', 'trip-republic', 'caddiehub', 'memolane', '1dollarthings.com', 'saveyourcall', 'mosoto', 'tweeturmusic', 'google-analytics-and-box.net', 'worlds-fastest-elevators', 'weather-web-app', 'places-near-me', 'quickresu.me', 'usa-name-data-bigquery-public-dataset', 'jacktracker-24', 'keeptherecord', 'funny-vines-thebestvines.tv', 'vodafone-update-app-android', 'asesor', 'mood-tweet', 'eyouin-notifications', 'moviis', 'klezio', 'belizemapia', 'mapping-events', 'friendlynx', 'popify', 'music-artist-cloud-app', 'facebook-funny-jokes', 'webaloud', 'imaginalaxy', 'birthdaygram', 'inflooenz', 'textorder.net', 'fitdatasync', 'lookupisbn.com', 'ergotxt', 'primocast', 'smslord', 'enomalism-elastic-computing', 'wikipedia-mobile', 'geosay-super-local-information', 'blizzalert-0', 'share-location-twitter', 'geopix-fractal-view', 'music-favmap', 'elseif', 'icommunity.tv', 'acid-reflux-information-site', 'sms-team', 'feedly-android', 'bluehire', 'pengerio', 'textmob', 'blizzalert', 'find-best-three', 'docs-pound-docs', 'watch2gether.com', 'music-artist-cloud-1', 'txt-beer', 'airporthotels', 'expressi', 'dynamic-insights', 'freshbooks-notifier', 'swoopthat', 'gmail-and-box.net', 'pinkbigmac', 'soho-rintaro', 'dfwdines-dfw-restaurant-week-guide', 'voicecal', 'worth-web', 'seo-audit-tool', 'earnlearn-web', 'offertrack', 'snapcasa-and-delicious-mashup', 'call-safely', 'gramfeed', 'teletka', 'gregs-alerts', 'jiffy-lyrics', 'readermeter', 'actionzap', 'relax', 'music-followers', 'sales-tracker', 'whtvrme', 'foursquare-check-deals', 'impact', 'refynr-social-dashboard-twiliocon-2012', 'travel-world-0', 'break-ice-me', 'english-lake-district', 'moredeets', 'how-to-pronounce-words-pronunciaci%C3%A3%C2%B3n-en-ingl%C3%A3%C2%A9s-pronuncia-inglese...', 'espocrm-0', 'utrecht-music-video-search', 'moonshadow-mobile-inc.', 'nitefly-future-nightlife', 'enterprisingly', 'google-maps-api-v3-tool', 'hotel-comparison-widget', 'tweedly-0', 'ivy-fm-discover-new-music-every-day', 'dog-parks-usa', 'mi-world', 'embedplus-chrome-browser-extension-youtube', 'connected', 'holidayen', 'storeslider-deutschland', 'allsongsby', 'musikki', 'svd-weather', 'nightfeed', 'beds-and-bedroom-news', 'magic-mosaic', 'just-traceroute', 'connectme.cc', 'platd', 'mapinterest', 'music-mash', 'spincloud', 'moomazon', 'earndit.com', 'photomunchrs', 'weogeo', 'sendmusic2.me', 'quizlio', 'daylogs', 'scaleo', 'eldercare-locator-phone-or-text-sms', 'goodneighbor', 'sendshorty', 'real-indoor', 'bookfinder', 'tripsq', 'amazon.com-gadget', 'fitstar', 'followfly', 'devhub', 'benzel-busch', 'embedplus', 'houseside', 'taggedback', 'profile-feeder', 'tapguest', 'our-louvre', 'songvoodoo', 'snapblast', 'tag-fight', 'flickrmania', 'relocator', 'spific-search', 'pictarine', 'rebate-bus', 'bookflavor', 'ministry-ops', 'iguide', 'tyke-sms-web-sms-gateway-and-more', 'printo.jp', 'info-balloon', 'northumberland-fold', 'misotrendy', 'tweetbrite', 'onnli.com-job-search-and-realtime-job-listing', 'ebooksdoc.com', 'instame', 'voice-apps', 'fonefindr', 'lunchbox', 'dormitem-free-college-classifieds', 'connecticity', 'whats-tv', 'wishalert.me', 'moodfm', 'second-life-weather', 'must-see-greece', 'square-anoia', 'incentify.it', 'toeat.com', 'l2-votermapping', 'golbal-hotel-price-map', 'social-map-california-colleges-universities', 'kickdash', 'lampsquare', 'taxi-and-rideshare-services-country', 'linda', 'poll-position', 'alert-boss-instant-customer-feedback-solution', 'reptiles-now', 'ariane-6', 'twiml-syntax-auto-complete-coda-plugin', 'map-deprivation-london', 'voxora', 'gatsby', 'weather-sentiment-prediction', 'hindi-songs-search', 'moveable-history', 'facebook-sentiment-analysis-tool', 'distance-calculator-entfernung.org', 'impact-dialing', 'usgolfers', 'ongmap', 'gocrowdless', 'college-and-university-search-state', 'scoopmap.net', 'populrbuys', 'yukon-live', 'gratefulapp', 'skaflash', 'lastnews', 'your-zodiac-sign-health-and-yoga', 'elasticlive-clustered-web-hosting', 'keep-jones', 'socialbro', 'snipper', 'belmonte-online', 'wikiorgcharts', 'i-am-here', 'flickstr', 'junctionvox', 'voice-slideshow-demo', 'flyfishmap', 'guardian-trends', 'youtube-vision', 'bbc-programmes-to-ical', 'geospeaker', 'onair-bus-tracker', 'sad-statements', 'otnettv-media-streaming-app', 'whats-twitter', 'big-picture-small-world', 'i-do-voices', 'mapmypage', 'domlia', 'youcheckins', 'call-company', 'filmfinder', 'online-basketball-camp', 'novels-location', 'photospots', 'bookfriend', 'sharemetric-chrome-extension', 'jars-love', 'world-facebook-friends.', 'mountains-world', 'social-contact', 'notifythem', 'pricezombie-price-tracker', 'ooyala', 'mapsavings.com', 'cab-dialer', 'popurls.com', 'yelp-search', 'voxpix', 'aimcrm', 'top-50-travel-locations', 'speed-phone-dating', 'zimride', 'hvper', 'vimasic', 'mashfot-mashup-about-photography', 'cbeams.org-deep-sky-objects-database', 'callrail', 'music-artist-cloud', 'my-friends-mosaic', 'vidscan', 'soccer-shots', 'picwash-photo-retouch-service', 'simplysubscribe.me', 'schoolandhousing', 'social-butterfly', 'glotter-maps', 'lyricstatus', 'cloud4smsviatwilio', 'timepost', 'delicious-preview', 'jozomello', 'craigslist-alerts', 'twitter-trends-explained', 'audiggle', 'youcall-md', 'golf-guide', 'buddyguard', 'dumpr.net', 'finda-park', 'textwhosnext', 'touropia', 'deli-tv-boxee', 'europass.me', 'google-contacts-map', 'travel-portal-solution', '4sqtransit', 'new-york-times-movie-tweets', 'gruvr-0', 'tripbuster.co.uk', 'twilio-mvc', 'netvibes-orb-quick-finder', 'wedgies', 'take-kerala-india', 'itooner', 'little-corner', 'weather-phone', 'real-time-simple-sms-voting-app', 'wattquiz', 'oggchat-live-customer-chat', 'youfm', 'loginradius', 'click2message', 'virtual-nyc-tour', 's3audible-music-and-video-streaming', 'callcollector', 'videva', 'wakey-wakey', 'newslinq', 'jobsyndicates', 'ringringbaby', 'twitter-trends-tagged', 'captcha-bypass-service', 'meedeor', 'smsmybus', 'down-or-not', 'indash-sms-dashboard-auto-responder-nexmo', 'retrotube', 'moviegram', 'citypockets-daily-deals', 'traffic-amigo', 'onair-air-app', 'hotelmapsearch.com', 'instashirt', 'mytube60-power-hour-videos', 'national-vip', 'song-pic', 'open-city-agora', 'minidates', 'psykotube', 'zaggle-zms', 'fitness-products', 'handmade-spark', 'gdrd', 'vodafone-update-app-blackberry-or-iphone', 'feedly-ios', 'esellerads', 'tagvy.com', 'distances-calculator', 'web-programming-jobs', 'christmas-list-app', 'overflown-countries', 'nodenock', 'worldsaurus.com-travel-guide', 'lokerku.web.id', 'country-search', 'explore-travellr', 'fuel-your-school-chevron', 'instalyrics', 'sportcentral', 'mp3-ja', 'loc.alize.us-flickr-mapped', 'twitea.me', 'tatildukkanicom', 'book-vs-movie', 'moremap', 'chapterboard', 'last.fm-missing-album-finder', 'supermetrics-data-grabber', 'loppee', 'gregs-pulse', 'caller-ig', 'twittercamp', 'collection-trakr', 'twizon', 'amazon-shopping-mashup', 'geomeme', 'probably-true', 'public-domain-reprints', 'httpbusalert.me', 'clickpoint', 'explore-to-yellow-pages', 'fly-time-notify', 'i-dont-need-no-stinking-phone', 'theinterviewr', 'mybill.', 'open-ftp', 'twitgraph', 'takeout-roulette', 'tweet-lot', 'movies-now-playing', 'mapa-del-paro', 'my-google', 'phoneco.', 'textweight', '4-1-search', 'beermap-top-2500-beers-twitter']
keep_set = set(keep_base_names)
# -----------------------------
# helpers
# -----------------------------
def strip_suffix_once(key: str, suffix: str = "-1") -> str:
    return key[:-len(suffix)] if key.endswith(suffix) else key


def parse_predicted_categories_from_reasoning(output_text: str) -> list:
    """
    reasoning output の末尾付近にある想定:
      recommend categories: [...]
    を雑に抽出する（失敗しても空リスト）
    """
    if not isinstance(output_text, str):
        return []

    m = re.search(r"recommend categories:\s*(\[[^\]]*\])", output_text, flags=re.IGNORECASE)
    if not m:
        return []

    raw = m.group(1)

    # '["a","b"]' / "['a','b']" / "[a, b]" に多少耐える
    items = re.findall(r"'([^']+)'|\"([^\"]+)\"|([a-z0-9_.\-/%]+)", raw, flags=re.IGNORECASE)
    cats = []
    for a, b, c in items:
        val = a or b or c
        if val:
            val = val.strip()
            if val and val.lower() != "none":
                cats.append(val)
    # 重複除去（順序維持）
    seen = set()
    out = []
    for x in cats:
        xl = x.lower()
        if xl not in seen:
            seen.add(xl)
            out.append(x)
    return out


# -----------------------------
# llm checker class
# -----------------------------
class make_few_open_llm:
    def __init__(self, available_categories, available_apis, service_requirements, correct_categories, correct_apis, reasoning_output):
        self.available_categories = available_categories
        self.available_apis = available_apis
        self.service_requirements = service_requirements
        self.correct_categories = correct_categories
        self.correct_apis = correct_apis
        self.reasoning_output = reasoning_output

        self.client = Client(
            host="http://localhost:11434",
            headers={"content-type": "application/json"}
        )

    def choice_prompt(self, prompt_method_name, model):
        prompt_method = getattr(self, prompt_method_name, None)
        if not prompt_method:
            raise ValueError(f"method {prompt_method_name} not found")

        messages = prompt_method()

        # ===== input確認用 =====
        print("\n===== llm input start =====")
        for i, msg in enumerate(messages):
            print(f"\n--- message {i} ---")
            print("role:", msg["role"])
            print(msg["content"])
        print("\n===== llm input end =====\n")
        # ======================

        try:
            response = self.client.chat(
                model=model,
                messages=messages,
                options={"temperature": 0}
            )
            return response.message.content
        except Exception as e:
            print(f"error: {e}")
            return None

    # -----------------------------
    # prompt: core vs category judgement
    # -----------------------------
    def judge_core_or_category_prompt(self):
        """
        Output strictly:
        label: one of [core_feature_error, category_error, no_error_or_unclear]
        reason: one short sentence
        evidence: short quotes (requirement + llm_output)
        """

        requirement_text = self.service_requirements
        reasoning_output = self.reasoning_output
        gt_categories = self.correct_categories

        system_text = (
            "You are an expert analyst of LLM reasoning processes for API recommendation. "
            "Your task is NOT to judge correctness, but to identify where the failure originated "
            "in a multi-step reasoning pipeline: core feature extraction (Step1) or category mapping (Step2). "
            "Follow the definitions strictly and do not make assumptions beyond the given texts."
        )

        user_text = f"""
    task:
    This service is known to be a FAILED case.
    Determine whether the failure was caused by:
    (1) incorrect core feature extraction, or
    (2) incorrect category mapping given reasonable core features.

    inputs:
    [requirement]
    {requirement_text}

    [llm_reasoning_output]
    {reasoning_output}

    [ground_truth_categories]
    {gt_categories}

    key idea (very important):
    - The question is NOT whether the chosen categories are correct.
    - The question IS whether the inferred core features could reasonably be mapped
    to the ground truth categories.

    definitions:
    - core_features_support_gt_category:
    The inferred core features are consistent with the requirement AND
    can naturally explain or justify the ground truth categories.

    decision rules (must follow in order):
    1) If the inferred core features are inconsistent with the requirement intent,
    OR they do NOT support mapping to the ground truth categories,
    output: core_feature_error.

    2) Else if the inferred core features are consistent with the requirement
    AND they DO support mapping to the ground truth categories,
    but the model selected different categories,
    output: category_error.

    3) Else if you cannot confidently decide either case,
    output: no_error_or_unclear.

    rules:
    - Do NOT judge API-level correctness.
    - Do NOT check whether chosen categories equal ground truth categories.
    - Judge only whether the core features make the ground truth categories reasonable.
    - If core features are too vague, generic, or underspecified to support the ground truth categories,
    treat this as NOT supporting them.
    - Do NOT guess. If uncertain, choose no_error_or_unclear.
    - You MUST include evidence quotes:
    - one short quote from the requirement
    - one short quote from the reasoning output
    (each <= 20 words)

    labels:
    - core_feature_error: core features are wrong or do not support the ground truth categories.
    - category_error: core features are reasonable and support the ground truth categories,
    but category mapping failed.
    - no_error_or_unclear: cannot confidently attribute the failure.

    output format (strict, exactly 3 lines):
    label: <core_feature_error | category_error | no_error_or_unclear>
    reason: <one short sentence>
    evidence: <quote from requirement> / <quote from llm_reasoning_output>
    """.strip()

        return [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ]

# -----------------------------
# load data
# -----------------------------
responses_path = "output/gpt_oss/few_cot_infer/responses.json"
mashup_path = "/home/matsumoto/llm_search2/data/filtered_mashup_data.json"

with open(responses_path, "r", encoding="utf-8") as f:
    raw_responses = json.load(f)

with open(mashup_path, "r", encoding="utf-8") as f:
    mashup_data = json.load(f)



# -----------------------------
# make mapping: service -> [reasoning_output, gt_categories, requirement_text]
# -----------------------------
output_with_gt_categories_and_req = {}

missing_in_mashup = []
bad_format = []

for key, output_text in raw_responses.items():
    service_name = strip_suffix_once(key)

    if service_name not in keep_set:
        continue

    if service_name not in mashup_data:
        missing_in_mashup.append(service_name)
        continue

    item = mashup_data[service_name]

    # item[1] -> requirement text
    # item[2] -> ground truth categories
    if not isinstance(item, list) or len(item) < 3:
        bad_format.append(service_name)
        continue

    requirement_text = item[1]
    gt_categories = item[2]

    output_with_gt_categories_and_req[service_name] = [output_text, gt_categories, requirement_text]

print("done")
print("final size:", len(output_with_gt_categories_and_req))
print("missing_in_mashup:", len(missing_in_mashup))
print("bad_format:", len(bad_format))

# -----------------------------
# run llm judgement for each service
# -----------------------------
# available_categories / available_apis / correct_apis は今回の判定では使わないが、
# クラスの形に合わせて渡す（空でok）
available_categories = []
available_apis = []
correct_apis = []

model = "gpt-oss:120b"  # 例: "llama3.1" などに置き換え

judgement_results = {}
failed_services = []

for service_name, (reasoning_output, gt_categories, requirement_text) in output_with_gt_categories_and_req.items():
    checker = make_few_open_llm(
        available_categories=available_categories,
        available_apis=available_apis,
        service_requirements=requirement_text,
        correct_categories=gt_categories,
        correct_apis=correct_apis,
        reasoning_output=reasoning_output
    )

    res = checker.choice_prompt("judge_core_or_category_prompt", model=model)
    if res is None:
        failed_services.append(service_name)
        continue

    judgement_results[service_name] = res


# -----------------------------
# save results (only outputs)
# -----------------------------
output_path = "output/gpt/few_cot_infer/judgement_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(judgement_results, f, ensure_ascii=False, indent=2)

print("llm judgement done")
print("judgement_results size:", len(judgement_results))
print("failed_services:", len(failed_services))
