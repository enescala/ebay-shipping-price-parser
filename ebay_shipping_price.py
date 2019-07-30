#!/usr/bin/env python

import csv
import random
import requests

from bs4 import BeautifulSoup


CSV_FILE = ''
SHOP_URL = ''

UA = [
    "Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/601.5.17 "
    "(KHTML, like Gecko) Version/9.1 Safari/601.5.17",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"
]

PRODUCTS = []


def parse_categories(page):
    min_cat_len = 120
    soup = BeautifulSoup(page, 'html.parser')
    categories = soup.find_all('li', class_='srp-refine__category__item')
    for category in categories:
        name = category.get_text().strip()
        url = category.find('a').get('href')
        if len(name) < min_cat_len:
            print(name)
            page = get_page(url)
            parse_products(page, name)
            pags = get_paginations(page)
            if pags:
                for num, url in enumerate(pags):
                    print('\tpaginated ', num + 1)
                    page = get_page(url)
                    parse_products(page, name)


def parse_products(page, category):
    soup = BeautifulSoup(page, 'html.parser')
    products = soup.find_all('li', class_='s-item')
    for product in products:
        product_url = product.find('a', class_='s-item__link').get('href')
        shipping_price = get_shipping_price(product_url)
        name = product.find('a', class_='s-item__link').get_text().strip()
        price = product.find('span', class_='s-item__price').get_text().strip()
        price, _ = price.split(' ')
        price = price.replace(',', '.')
        name = name.replace('"', '&quot;')
        PRODUCTS.append([category, name, price, shipping_price])


def get_shipping_price(url):
    base_price = 0.0
    page = get_page(url)
    soup = BeautifulSoup(page, 'html.parser')
    price_full = soup.find('span', id='fshippingCost')

    if price_full:
        price_full = price_full.get_text().strip()
    else:
        return base_price

    if ' ' in price_full:
        price, _ = price_full.split(' ')
        price = price.replace(',', '.')
    else:
        price = base_price

    return price


def get_paginations(page):
    result = []
    soup = BeautifulSoup(page, 'html.parser')
    pagination = soup.find_all('li', class_='ebayui-pagination__li')
    for pag in pagination:
        if 'ebayui-pagination__li--selected' not in str(pag):
            url = pag.find('a').get('href')
            result.append(url)
    return result


def get_page(url):
    print(url)
    try:
        r = requests.get(url, headers={'User-Agent': random.choice(UA)})
        status = r.status_code
        if status == 200:
            return r.text
    except requests.exceptions.RequestException as e:
        print("Error: {} {}".format(e, url))
    return None


def save_file(filename):
    with open(filename, 'w') as f:
        dw = csv.writer(f, delimiter='#', quoting=csv.QUOTE_NONE, escapechar='', quotechar='')
        for product in PRODUCTS:
            dw.writerow(product)


def main():
    page = get_page(SHOP_URL)
    parse_categories(page)
    save_file(CSV_FILE)


main()
