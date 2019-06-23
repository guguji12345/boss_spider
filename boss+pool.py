import requests
from lxml import etree
import csv


headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        "referer":"https://www.zhipin.com/job_detail/?query=python%E7%88%AC%E8%99%AB&city=101270100&industry=&position="
    }

def get_proxy():
    url = 'http://127.0.0.1:5555/random'
    response = requests.get(url)
    text = response.content.decode("utf-8")
    proxy = {
        "http":"http://"+text,
        "https":"https://"+text
    }
    return proxy

def parse_page(url):
    works = []
    proxy = get_proxy()
    while True:
        try:
            response = requests.get(url,headers=headers,proxies=proxy,timeout=5)
            text = response.content.decode("utf-8")
            html = etree.HTML(text)
            lis = html.xpath("//div[@class='job-list']/ul/li")
            if lis !=[]:
                print("页面处当前代理可用,为%s"%proxy)
                break
            else:
                print("页面处%s代理已被封禁" % proxy)
                proxy = get_proxy()
                print("页面处更换代理为%s重试" % proxy)
        except:
            print("页面处%s代理请求超时"%proxy,end = ',')
            proxy = get_proxy()
            print("页面处更换代理为%s重试" % proxy)
    for li in lis:
        href = li.xpath(".//div[@class='info-primary']/h3[@class='name']/a/@href")[0]
        detail_url = "https://www.zhipin.com"+href
        parse_detail(detail_url,works,proxy)
        proxy = proxy
    save(works)
    next_href = html.xpath("//div[@class='page']/a[last()]/@href")
    print(next_href)
    if next_href !=[]:
        next_href = "https://www.zhipin.com"+next_href[0]
        parse_page(next_href)
    else:
        pass

def parse_detail(url,works,proxy):
    work_info = {}
    work_info["工作详情页"] = url
    while True:
        try:
            response = requests.get(url, headers=headers,proxies=proxy,timeout=5)
            text = response.content.decode("utf-8")
            html = etree.HTML(text)
            name = html.xpath("//div[@class='info-primary']/div[@class='name']/h1/text()")
            if name !=[]:
                print("详情处当前代理可用,为%s"%proxy)
                break
            else:
                print("详情处%s代理已被封禁" % proxy,end = ',')
                proxy = get_proxy()
                print("详情处更换代理为%s重试"%proxy)
        except:
            print("详情处%s代理请求超时" % proxy,end = '')
            proxy = get_proxy()
            print("详情处更换代理为%s" % proxy)
    work_info["工作名"]=name[0]
    wage = html.xpath("//div[@class='info-primary']/div[@class='name']/span/text()")[0]
    work_info["工资"]=wage
    message = html.xpath("//div[@class='job-primary detail-box']//div[@class='info-primary']/p//text()")
    place = message[0]
    work_info["工作地点"]=place
    experience = message[1]
    work_info["经验要求"]=experience
    education = message[2]
    work_info["学历要求"]=education
    welfare = html.xpath("//div[@class='info-primary']//div[@class='job-tags']//text()")
    welfare = ",".join(welfare[1:-1])
    work_info["福利"]=welfare
    work = html.xpath("//div[@class='job-sec']/div[@class='text']//text()")
    work = "".join(work).replace("\xa0","").replace("\n","").replace(" ","").strip()
    work_info["工作详情"]=work
    company = html.xpath("//div[@class='company-info']/a[2]/text()")
    company = "".join(company).replace("\n","").replace("\xa0","").replace(" ","").strip()
    work_info["公司名"]=company
    print(work_info)
    works.append(work_info)
    return works

def save(works):
    header = ["工作详情页","公司名","工作名","工资","工作地点","经验要求","学历要求","福利","工作详情"]
    with open("boss_work.csv", "a", encoding="utf-8", newline="")as f:
        writer = csv.DictWriter(f,header)
        writer.writeheader()
        writer.writerows(works)

if __name__ == '__main__':
    url = 'https://www.zhipin.com/c100010000/?query=python%E7%88%AC%E8%99%AB&ka=sel-city-100010000'
    parse_page(url)