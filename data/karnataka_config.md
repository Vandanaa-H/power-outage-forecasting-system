# Karnataka Power Outage Forecasting - Data Configuration

## Target Cities (High Priority based on population and industrial activity)

### Tier 1 Cities (Highest Priority)
- **Bangalore Urban** (12.3M population, IT hub)
- **Bangalore Rural** (991K population, industrial)
- **Mysore** (3M population, heritage city)
- **Hubli-Dharwad** (1.8M population, commercial center)

### Tier 2 Cities (High Priority)
- **Mangalore** (623K population, port city)
- **Belgaum** (610K population, border trade)
- **Gulbarga** (543K population, railway junction)
- **Davangere** (434K population, cotton center)
- **Bellary** (410K population, mining hub)
- **Bijapur** (327K population, agricultural center)

### Rural Focus Areas
- **Coastal Karnataka** (Monsoon-prone, frequent outages)
- **North Karnataka** (Drought-prone, irrigation pumps)
- **Western Ghats** (Heavy rainfall, landslides affecting power)
- **Agricultural Districts** (Seasonal power demand patterns)

## Data Sources Priority

### 1. Historical Outage Data
- Karnataka Power Corp Limited (KPTCL) grid data
- BESCOM (Bangalore) - highest priority
- MESCOM (Mangalore) - coastal region
- HESCOM (Hubli-Dharwad) - north Karnataka  
- GESCOM (Gulbarga) - northeast Karnataka

### 2. Weather Data Sources
- IMD Bangalore (Primary weather station)
- OpenWeather API (Real-time + historical)
- Monsoon tracking (June-September critical)
- Lightning detection networks

### 3. Load Pattern Data
- Industrial load patterns (IT parks, manufacturing)
- Agricultural load patterns (irrigation pumps)
- Residential load patterns (urban vs rural)
- Seasonal variations (summer cooling, monsoon pumps)

## Geographic Zones for Modeling

### Zone 1: Bangalore Metropolitan (Ultra High Priority)
- BESCOM coverage area
- IT corridor outages = massive economic impact
- Urban infrastructure stress

### Zone 2: Coastal Karnataka (High Weather Risk)
- MESCOM coverage
- Monsoon vulnerability
- Port and industrial activity

### Zone 3: North Karnataka (Agricultural + Commercial)
- HESCOM + GESCOM coverage
- Drought/irrigation impacts
- Commercial activity centers

### Zone 4: South Karnataka (Heritage + Tourism)
- Mysore region
- Tourism infrastructure
- Agricultural processing
