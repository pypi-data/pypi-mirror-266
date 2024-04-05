<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/flairNLP/fundus/blob/master/resources/logo/svg/logo_darkmode_with_font_and_clear_space.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/flairNLP/fundus/blob/master/resources/logo/svg/logo_lightmode_with_font_and_clear_space.svg">
    <img src="https://github.com/flairNLP/fundus/blob/master/resources/logo/svg/logo_lightmode_with_font_and_clear_space.svg" alt="Logo" width="50%" height="50%">
  </picture>
</p>

<p align="center">A very simple <b>news crawler</b> in Python.
Developed at <a href="https://www.informatik.hu-berlin.de/en/forschung-en/gebiete/ml-en/">Humboldt University of Berlin</a>.
</p>
<p align="center">
<img alt="version" src="https://img.shields.io/badge/version-0.1-green">
<img alt="python" src="https://img.shields.io/badge/python-3.8-blue">
<img alt="Static Badge" src="https://img.shields.io/badge/license-MIT-green">
<img alt="Publisher Coverage" src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/dobbersc/ca0ae056b05cbfeaf30fa42f84ddf458/raw/fundus_publisher_coverage.json">
</p>
<div align="center">
<hr>

[Quick Start](#quick-start) |  [Tutorials](#tutorials)  | [News Sources](/docs/supported_publishers.md)

</div>


---

Fundus is:

* **A static news crawler.** 
  Fundus lets you crawl online news articles with only a few lines of Python code!
  Be it from live websites or the CC-NEWS dataset.

* **An open-source Python package.**
  Fundus is built on the idea of building something together. 
  We welcome your contribution to  help Fundus [grow](docs/how_to_contribute.md)!

<hr>

## Quick Start

To install from pip, simply do:

```
pip install fundus
```

Fundus requires Python 3.8+.


## Example 1: Crawl a bunch of English-language news articles

Let's use Fundus to crawl 2 articles from publishers based in the US.

```python
from fundus import PublisherCollection, Crawler

# initialize the crawler for news publishers based in the US
crawler = Crawler(PublisherCollection.us)

# crawl 2 articles and print
for article in crawler.crawl(max_articles=2):
    print(article)
```

That's already it!

If you run this code, it should print out something like this:

```console
Fundus-Article:
- Title: "Feinstein's Return Not Enough for Confirmation of Controversial New [...]"
- Text:  "Democrats jammed three of President Joe Biden's controversial court nominees
          through committee votes on Thursday thanks to a last-minute [...]"
- URL:    https://freebeacon.com/politics/feinsteins-return-not-enough-for-confirmation-of-controversial-new-hampshire-judicial-nominee/
- From:   FreeBeacon (2023-05-11 18:41)

Fundus-Article:
- Title: "Northwestern student government freezes College Republicans funding over [...]"
- Text:  "Student government at Northwestern University in Illinois "indefinitely" froze
          the funds of the university's chapter of College Republicans [...]"
- URL:    https://www.foxnews.com/us/northwestern-student-government-freezes-college-republicans-funding-poster-critical-lgbtq-community
- From:   FoxNews (2023-05-09 14:37)
```

This printout tells you that you successfully crawled two articles!

For each article, the printout details:
- the "Title" of the article, i.e. its headline 
- the "Text", i.e. the main article body text
- the "URL" from which it was crawled
- the news source it is "From"


## Example 2: Crawl a specific news source

Maybe you want to crawl a specific news source instead. Let's crawl news articles from Washington Times only:

```python
from fundus import PublisherCollection, Crawler

# initialize the crawler for Washington Times
crawler = Crawler(PublisherCollection.us.WashingtonTimes)

# crawl 2 articles and print
for article in crawler.crawl(max_articles=2):
    print(article)
```

## Example 3: Crawl articles from CC-NEWS

If you're not familiar with CC-NEWS, check out their [paper](https://paperswithcode.com/dataset/cc-news).

````python
from fundus import PublisherCollection, CCNewsCrawler

# initialize the crawler for news publishers based in the US
crawler = CCNewsCrawler(*PublisherCollection.us)

# crawl 2 articles and print
for article in crawler.crawl(max_articles=2):
  print(article)
````


## Tutorials

We provide **quick tutorials** to get you started with the library:

1. [**Tutorial 1: How to crawl news with Fundus**](docs/1_getting_started.md)
2. [**Tutorial 2: How to crawl articles from CC-NEWS**](docs/2_crawl_from_cc_news.md)
3. [**Tutorial 3: The Article Class**](docs/3_the_article_class.md)
4. [**Tutorial 4: How to filter articles**](docs/4_how_to_filter_articles.md)
5. [**Tutorial 5: How to search for publishers**](docs/5_how_to_search_for_publishers.md)

If you wish to contribute check out these tutorials:
1. [**How to contribute**](docs/how_to_contribute.md)
2. [**How to add a publisher**](docs/how_to_add_a_publisher.md)

## Currently Supported News Sources

You can find the publishers currently supported [**here**](/docs/supported_publishers.md).

Also: **Adding a new publisher is easy - consider contributing to the project!**

## Contact

Please email your questions or comments to [**Max Dallabetta**](mailto:max.dallabetta@googlemail.com?subject=[GitHub]%20Fundus)

## Contributing

Thanks for your interest in contributing! There are many ways to get involved;
start with our [contributor guidelines](docs/how_to_contribute.md) and then
check these [open issues](https://github.com/flairNLP/fundus/issues) for specific tasks.

## License

[MIT](LICENSE)
