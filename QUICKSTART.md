# Quick Start Guide - Cricbuzz LiveStats

## 🚀 5-Minute Setup

### Step 1: Navigate to Project Directory
```bash
cd d:\test\cricbuzz_app
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key
Create `.streamlit/secrets.toml` with your RapidAPI key:
```toml
RAPIDAPI_KEY = "your_key_here"
```

Or use the provided default (already in `.streamlit/secrets.toml`):
```toml
RAPIDAPI_KEY = "5ff5c15309msh270be5dd89152b5p1f3d98jsnf270423b3863"
```

### Step 4: Run the Application
```bash
streamlit run main.py
```

The app will open at: `http://localhost:8501`

---

## 📖 User Guide

### Home Page (🏠)
- Overview of the project
- Business use cases
- Technical stack
- Quick navigation links

### Live Matches (⚡)
- **Select Match Type**: Live, Upcoming, or Recent
- **Auto-refresh**: Set refresh interval
- **View Details**: Expand series to see all matches
- **Scorecard**: Click "View Scorecard" button for detailed match info

### Player Stats (📊)
- **All Players**: View complete player database
- **Top Batsmen**: Ranking by runs, average, centuries, strike rate
- **Top Bowlers**: Ranking by wickets, average, economy rate
- **Player Details**: Individual player statistics and trends

### SQL Analytics (🔍)
1. **Select Difficulty**: Beginner, Intermediate, or Advanced
2. **Choose Query**: Select from 25 available queries
3. **View SQL**: Expand to see the SQL code
4. **Execute**: Click "Execute Query" button
5. **Results**: View results and download as CSV

#### All 25 Queries Available:
- **Beginner (1-8)**: Basic SELECT, WHERE, GROUP BY operations
- **Intermediate (9-16)**: JOINs, subqueries, aggregations
- **Advanced (17-25)**: Window functions, CTEs, complex analytics

### CRUD Operations (🛠️)
#### Players Management
- ➕ **Create**: Add new players with role and style
- 📖 **Read**: View all players in database
- ✏️ **Update**: Modify player statistics
- 🗑️ **Delete**: Remove player records

#### Matches Management
- ➕ **Create**: Add new match records
- 📖 **Read**: View all matches with details
- ✏️ **Update**: Update match results

#### Venues Management
- ➕ **Create**: Add new cricket venues
- 📖 **Read**: View all venues

---

## 🎮 Sample Data

The app comes with sample data for demonstration:
- 6 players (Kohli, Smith, Williamson, Azam, Root, Warner)
- 6 bowlers (Bumrah, Cummins, Boult, Rabada, Wood, Starc)
- Sample match statistics and venues

---

## 💾 Database

### Auto-created SQLite Database
- **File**: `cricbuzz.db`
- **Tables**: 6 (players, matches, venues, innings, batsmen, bowlers)
- **Auto-initialized**: Database and schema created on first run

### Tables Structure
1. `players` - Player information and statistics
2. `matches` - Match details and results
3. `venues` - Cricket ground information
4. `innings` - Inning-level data
5. `batsmen` - Individual batting performances
6. `bowlers` - Individual bowling performances

---

## 🔧 Troubleshooting

### Issue: "Module not found" error
**Solution**: Install missing packages
```bash
pip install -r requirements.txt
```

### Issue: API key error
**Solution**: Verify `.streamlit/secrets.toml` has valid RAPIDAPI_KEY
```toml
RAPIDAPI_KEY = "your_key_here"
```

### Issue: Database locked
**Solution**: Close other connections to `cricbuzz.db`
```bash
rm cricbuzz.db
# Restart app - will recreate automatically
```

### Issue: Port 8501 already in use
**Solution**: Run on different port
```bash
streamlit run main.py --server.port 8502
```

---

## 📊 Features Checklist

- [x] Real-time match updates (Live/Upcoming/Recent)
- [x] Player statistics with visualizations
- [x] 25 SQL practice queries (all difficulty levels)
- [x] Full CRUD operations for players, matches, venues
- [x] Scorecard fetching and display
- [x] Auto-creating SQLite database
- [x] CSV export functionality
- [x] Multi-page Streamlit navigation
- [x] Responsive UI with custom styling
- [x] Comprehensive documentation

---

## 🎓 Learning Resources

### SQL Query Types Covered
1. **Basic Queries**: SELECT, WHERE, ORDER BY, GROUP BY
2. **Joins**: INNER JOIN, LEFT JOIN
3. **Subqueries**: Nested SELECT statements
4. **Aggregations**: COUNT, SUM, AVG, MAX, MIN
5. **Window Functions**: RANK, ROW_NUMBER, LAG
6. **CTEs**: Common Table Expressions
7. **Case Statements**: CASE WHEN logic
8. **Date Functions**: DATE, STRFTIME

### API Integration
- REST API calls using `requests` library
- JSON response parsing
- Error handling and retry logic
- Rate limiting considerations

### Database Operations
- Schema design and normalization
- CRUD operations
- Query optimization
- Data integrity

---

## 📞 Support Resources

### Getting Help
1. **Read README.md** - Comprehensive documentation
2. **Check Error Messages** - Clear error descriptions
3. **View Sample Queries** - SQL query examples
4. **Inspect API Responses** - JSON debug output

### Reporting Issues
- Check `.streamlit/logs.txt` for detailed logs
- Verify all dependencies are installed
- Test with sample data first
- Ensure API key is valid

---

## 🚀 Next Steps

1. ✅ Complete the setup above
2. ✅ Explore each section of the app
3. ✅ Run sample queries
4. ✅ Add your own players/matches
5. ✅ Customize and extend functionality

---

## 📝 Tips & Tricks

### Database Management
```bash
# Backup database
cp cricbuzz.db cricbuzz_backup.db

# Clear database (will recreate on restart)
rm cricbuzz.db
```

### Development
```bash
# Run with debug output
streamlit run main.py --logger.level=debug

# Run on different port
streamlit run main.py --server.port 8502
```

### Performance
- SQL queries cache results automatically
- API responses cached for 1 hour
- Database uses indices for faster queries

---

**Happy Exploring! 🏏📊**

For detailed documentation, see `README.md`
