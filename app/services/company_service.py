from app.services.db import get_collection
from app.models import CompanyInfo
from typing import List

def get_companies() -> List[CompanyInfo]:
    collection = get_collection()
    
    # We fetch only metadatas to find all distinct companies and years
    result = collection.get(include=["metadatas"])
    metadatas = result.get("metadatas", [])
    
    companies_data = {}
    
    for meta in metadatas:
        ticker = meta.get("ticker", "").upper()
        if not ticker:
            continue
            
        year = str(meta.get("fiscal_year"))
        
        if ticker not in companies_data:
            companies_data[ticker] = set()
            
        companies_data[ticker].add(year)
        
    company_list = []
    for ticker, years in companies_data.items():
        # Hardcode some names for a better UX based on known tickers
        name = ticker
        company_names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "TSLA": "Tesla, Inc.",
            "NVDA": "NVIDIA Corporation",
            "AMZN": "Amazon.com, Inc.",
            "GOOGL": "Alphabet Inc.",
            "META": "Meta Platforms, Inc.",
            "JPM": "JPMorgan Chase & Co.",
            "KO": "The Coca-Cola Company",
            "WMT": "Walmart Inc.",
            "NFLX": "Netflix, Inc.",
            "ORCL": "Oracle Corporation"
        }
        if ticker in company_names:
            name = company_names[ticker]
        
        company_list.append(
            CompanyInfo(
                ticker=ticker,
                name=name,
                years=sorted(list(years))
            )
        )
        
    return sorted(company_list, key=lambda x: x.ticker)
