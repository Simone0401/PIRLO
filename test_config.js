await fetch("http://localhost:10000/", {
    "credentials": "include",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i"
    },
    "referrer": "http://localhost:10000/",
    "body": "csrf_token=IjhhYzRmYTJhMzA0MjZmNjJjMjdkZTQzM2M2YTIwNjUwMzNmYzAxYTIi.aFwdVQ.fH1wLhDtVCMbxMEHAA0O_rqohmw&vm_ip=127.0.0.1&vm_port=2222&vm_password=rootpassword&team=30&number_of_teams=40&team_token=5b1573806780916812af4c4fa5f30e3b&start_round=2025-06-25T18%3A01&training=y&traffic_dir_host=%2FUsers%2Fsimone%2FDesktop%2FUniversita%2FCyberChallenge2025%2FAD",
    "method": "POST",
    "mode": "cors"
});