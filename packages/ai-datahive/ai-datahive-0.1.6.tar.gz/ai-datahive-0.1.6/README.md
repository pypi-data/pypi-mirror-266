# AI Enhanced DataHive

## Introduction

AI Enhanced DataHive embarks on a mission to become a centralized hub for data of various kinds, offering templates for collectors to aggregate data centrally for further processing in other applications. This initiative arises from the repeated cycles of developing crawlers, extractors, and collectors across numerous projects. Developers often reimplement or reuse functions throughout their codebase, leading to inefficient data handling practices like multiple downloads of the same data or the constant need to create new platforms for data storage.

It used a classical ETL approach to collect data from various sources, transform it into unified formats and load them to be published by some sort of publisher.
Every steps is separat, so that you can easily replace the collector, transformer or publisher with your own implementation.

By providing a unified solution, AI Enhanced DataHive aims to simplify the development of numerous projects, for instance, those based on research reports from Arxiv, by making centrally available data readily accessible.

## Why AI Enhanced DataHive?

- **Centralized Data Collection**: Offers a singular point for aggregating data from diverse sources, eliminating the redundancy of data collection efforts across projects.
- **Supabase for Storage**: Utilizes Supabase for data storage, offering a free starting point without the hassle of hosting or setup, ensuring a swift implementation process.
- **DAO Pattern**: Employs the DAO (Data Access Object) pattern, allowing for easy substitution of Supabase with alternative storage solutions to meet the varying requirements of different projects.
- **Data Processing**: Beyond storage, the platform will facilitate processes to further refine collected data, making it ready for subsequent utilization.
- **Technology Breakthrough**: The initial technological achievement of DataHive is its ability to convert collected information into news items, disseminated via a Telegram bot in a group setting.

Designed initially for AI news, the framework's flexibility through additional collectors and transformers makes it easily adaptable for other Telegram groups, mailing lists, websites, and similar publishing channels.

## Collector Implementations

- **Arxiv**: Collects research papers from Arxiv, a preprint repository for physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, systems science, and economics.
- **CivitAI**: Collects image from CivitAI, a platform for AI generated images.
- **Github**: Collects trending repositories from Github.
- **Zotero**: Collects entries of collection from a private Zotero library.

## Transformer Implementations

- **TopDailyImage**: Transforms CivitAI images into a daily top image Content piece.
- **DailyArxivPaper**: Transforms Daily Arxiv paper into a daily research paper Content piece.
- **DailyTrendingGitHub**: Transforms Daily Github projects into a daily github Content piece.

## Publisher Implementations

- **Telegram**: A loader transforms content pieces into telegram messages that are published into a group by a bot.
  - Daily Images, Daily Papers, Daily Trending Github Projects 

## Prerequisites
Python 3.10 or higher\
Supabase Account (or implement the BaseDAO to use another storage solution)\
Zotero Account (if you like to use the Zotero Collector)\
Telegram Group (with Topics) and a Bot (if you like to use the Telegram Publisher)

## Getting Started

To incorporate AI Enhanced DataHive into your project, follow these steps:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/bizrockman/AI-Enhanced-DataHive.git   

2. **Install the Dependencies**

   ```bash
    cd AI-Enhanced-DataHive
    pip install -r requirements.txt

3. **Configuration**

   Set up your environment with the required API keys and settings in the `.env` file for seamless integration with Supabase and other services.

   For that copy the template `.env.example` to `.env` and fill in the required details.


4. **Setting up Supabase**

   Create a new project on [Supabase](https://supabase.io/), and set up the required tables and columns as per the 
   schemata provided in the the directory `db`.


5. **Run the Collector**

   Run all collectors of your choice using the following command. Configured for CivitAI Collector right now:

   ```bash
   python main.py
   ```
   
## Remarks

The project is an early concept and is under active development. So things will change and the code base is not stable 
or perfect yet. This is the first proof of concept.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, feel free to open an issue or contact me on [LinkedIn](https://www.linkedin.com/in/dannygerst/).

[