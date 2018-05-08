import bs4 as bs
import urllib.request
import webbrowser
import os
import re

keywords = input("Enter keywords separated by commas: ").split(",")
pages = int(input("Enter number of pages to parse: "))
print ("\nRunning ...\n")
keywords[:] = [keyword for keyword in keywords if keyword.strip() != ""]
#OPEN FILE
file = open("search_results.html", "wb")
file.write("<html><head><style>div.groove {border-style:groove; padding:15px; margin:15px; border-color:#92a8d1;}</style></head><body>".encode('ascii', 'replace'))

#PRICE CHECK (OPEN BEAUTIFULSOUP)
hdr = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request("http://rl.insider.gg/pc",headers=hdr)
sauce = urllib.request.urlopen(req).read()
soup = bs.BeautifulSoup(sauce,'lxml')

print("Retrieving prices for: ",end="")
price_entry = ["<div class=\"groove\"><h2>Hover to view prices:</h2>","</div>"]
count = 0
for tr in soup.find_all('tr', attrs={'class': 'itemRow'}):
    try:
        for keyword in keywords:
            if keyword.lower().strip() in tr['data-itemfullname'].lower():
                count += 1
                if count == 1:
                    print(tr['data-itemfullname'],end="")
                else:
                    print((", " + tr['data-itemfullname']),end="")
                to_add = "<h4 title=\""
                #SKIP FIRST ENTRY
                iter_tr = iter(tr)
                next(iter_tr)
                for td in iter_tr:
                    to_add += td.get('class')[0].replace('price','') + ": " + td.text.replace('&hairsp;','') + "\n"
                to_add += "\">" + tr['data-itemfullname'] + "</h4>"
                price_entry.append(to_add)
    except KeyError:
        print("",end="")

if count == 0:
    print("<none>\n")
    price_entry = ['']
file.write(price_entry[0].encode('ascii', 'replace'))
if count != 0:
    print("\n")
    for price_row in price_entry[2:]:
        file.write(price_row.encode('ascii', 'replace'))
    file.write(price_entry[1].encode('ascii', 'replace'))

# Receive links for all posts
links = []
page_index = 0
results = 1
if len(keywords) > 0:
    while page_index < pages:
        print("Retrieving links from page " + str(page_index + 1) + " ...")
        sauce = urllib.request.urlopen('https://steamcommunity.com/app/252950/tradingforum/' + '?fp=' + str(page_index + 1)).read()
        soup = bs.BeautifulSoup(sauce,'lxml')
        for a in soup.find_all('a'):
            if(a.get('class') != None and a.get('class')[0]=="forum_topic_overlay"):
                links.append(a.get('href'))
        # Go to next page of posts
        page_index += 1
    print("\nREADY")
else:
    print("Found no valid keywords.")

# LOOPING THROUGH LINKS
i = 0
while i < len(links):
    if i == 0:
        i = 2
    post = urllib.request.urlopen(links[i]).read()
    new_soup = bs.BeautifulSoup(post,'lxml')
    entry = ['']
    html_entry = []

    # GRAB USER INFO
    for a in new_soup.find_all('a', attrs={'class': 'forum_op_author'}):
        entry.append(str(results) + ".")
        html_entry.append("<p><a href=\"" + a.get('href') + "\">" + a.text.strip() + "</a>")
        entry.append("Poster             | " + a.text.strip())
        entry.append("Poster's Profile   | " + a.get('href'))
    for span in new_soup.find_all('span', attrs={'class': 'date'}):
        entry.append("Time Posted        | " + span.text.strip())
        html_entry.append(" - " + span.text.strip() + "<br/>")
    for div in new_soup.find_all('div', attrs={'class': 'forum_paging_summary'}):
        html_entry.append("Comments: " + div.find_all('span')[2].text.strip())
        break
    entry.append("Link to Post       | " + links[i])

    # POST HEADER
    keyword_in_title = False
    for div in new_soup.find_all('div', attrs={'class': 'topic'}):
        if div != None:
            entry.append("Post Title         | " + div.text.strip())
            html_entry.append("<div class=\"groove\"><h3><a href=\"" + links[i] + "\">" + str(results) + ". " + div.text.strip() + "</a></h3>")
            for keyword in keywords:
                if keyword.lower().strip() in div.text.lower():
                    keyword_in_title = True
                    break

    # POST BODY
    keyword_in_body = False
    body = ""
    for div in new_soup.find_all('div', attrs={'class': 'content'}):
        if (div != None and next(div.parents).get('class')==['forum_op']):
            row_count = 0;
            for row in list(div.stripped_strings):
                for keyword in keywords:
                    keyword_re = re.compile(re.escape(keyword.strip()),re.IGNORECASE)
                    if keyword.lower().strip() in row.lower():
                        body = "Post Body (ln " + str(row_count + 1) + ")"
                        for x in range (len(str(row_count)), 4):
                            body += " "
                        body += "| "
                        entry.append(body + row)
                        html_entry.append(body + keyword_re.sub(("<b>" + keyword.strip().upper() + "</b>"), row))
                        keyword_in_body = True
                        break
                row_count += 1;

    # Check and see if one of the flags were set and print if they were.
    if keyword_in_body or keyword_in_title:
        results += 1
        for entry_row in entry:
            print(entry_row)
        file.write(html_entry[3].encode('ascii', 'replace'))
        file.write(html_entry[0].encode('ascii', 'replace'))
        file.write(html_entry[1].encode('ascii', 'replace'))
        file.write(html_entry[2].encode('ascii', 'replace'))
        if keyword_in_body:
            for body_row in html_entry[4:]:
                file.write(("<br/>" + body_row).encode('ascii', 'replace'))
            file.write("<br/></p></div>".encode('ascii','replace'))
        else:
            file.write("<br/></p></div>".encode('ascii','replace'))
    # INDEX
    i += 1

file.write("</html></body>".encode('ascii', 'replace'))

if results > 1:
    url = 'file://' + os.getcwd() + '/search_results.html'
    webbrowser.open(url, new=2)
print("\nFound " + str(results - 1) + " results. Ending program ...")
