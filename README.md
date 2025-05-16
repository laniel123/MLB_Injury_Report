
# Dodgers Injury Report

The **Dodgers Injury Report** is a Python-based tool designed to scrape, track, and manage injury data for Los Angeles Dodgers players. It automates the collection of injury reports and player information, storing them in a structured SQLite database for easy access and analysis.

## Features

- Scrapes the latest injury reports from [MLB.com](https://www.mlb.com/news/dodgers-injuries-and-roster-moves)
- Extracts player details from the Dodgers' official 40-man roster
- Stores data in a local SQLite database for efficient querying
- Provides a command-line interface for data updates and logging

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/laniel123/Dodgers_Injury_Report.git
   cd Dodgers_Injury_Report
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script to begin scraping and updating data:

```bash
python main.py
```

This will:
- Scrape the latest injury reports and player info
- Update the local SQLite database
- Log scraping operations to `logs/injury_log.txt`

## Project Structure

```
Dodgers_Injury_Report/
├── data/
│   └── dodgers_injury_db.sqlite    # SQLite database
├── logs/
│   └── injury_log.txt              # Log file for injury updates
├── scraper/
│   ├── base_scraper/
│   │   └── injury.py               # Scrapes MLB injury news
│   └── player_info/
│       └── player_info.py          # Scrapes Dodgers roster info
├── main.py                         # Main entry point
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

## Contributing

Contributions are welcome! To contribute:

1. Fork this repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a pull request

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [MLB.com](https://www.mlb.com/) for injury and player data
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Requests](https://docs.python-requests.org/) for HTTP requests
