# Q&A Enhanced Features

## Overview
The Q&A system now retrieves answers directly from your uploaded CSV data instead of only using the LLM. This means instant, accurate answers without API credits.

## How It Works

### Priority Order:
1. **Direct Data Retrieval** (primary) - Searches your CSV/dataframe
2. **LLM Response** (fallback) - Uses OpenRouter if data retrieval doesn't match
3. **Context-Based Answer** (final fallback) - Uses analysis insights if LLM credits exhausted

## Supported Question Types

### 1. **Maximum/Highest Values**
Ask: "What is the maximum sales?"
Answer: Returns actual max value from the data

Examples:
- "What is the max salary?"
- "Show me the highest revenue"
- "Maximum value in profit column"

### 2. **Minimum/Lowest Values**
Ask: "What is the minimum sales?"
Answer: Returns actual min value from the data

Examples:
- "What is the lowest price?"
- "Minimum salary in the dataset"
- "Smallest value in quantity"

### 3. **Average/Mean Values**
Ask: "What is the average sales?"
Answer: Returns calculated mean

Examples:
- "What is the average salary?"
- "Mean revenue by region"
- "Average price in inventory"

### 4. **Count/Total Records**
Ask: "How many records are in the dataset?"
Answer: Returns total row count

Examples:
- "Total records in database"
- "How many entries?"
- "Count of all rows"

### 5. **Unique/Distinct Values**
Ask: "What are the unique categories?"
Answer: Shows distinct values and count

Examples:
- "Show me unique departments"
- "Different product types"
- "Distinct regions in data"

### 6. **Column Information**
Ask: "Tell me about the sales column"
Answer: Shows statistics and samples

Examples:
- "Describe the products column"
- "What's in the dates field?"
- "Details about price column"

### 7. **Filtering/Conditional Queries**
Ask: "Show me records where revenue > 1000"
Answer: Returns filtered results

Examples:
- "Employees with salary > 50000"
- "Products priced above 100"
- "Sales in the top 10%"

## Key Benefits

✅ **No API Credits Needed** - Data retrieval works offline  
✅ **Instant Responses** - No LLM latency  
✅ **100% Accurate** - Direct from your data  
✅ **Works Offline** - When LLM is unavailable  
✅ **Smart Fallback** - Attempts LLM if exact match not found  

## Example Questions and Answers

**Q:** "What is the maximum sales?"
**A:** 📊 **Maximum sales**: 45000
This is the highest value in the sales column of your dataset.

---

**Q:** "How many records?"
**A:** 📊 **Total Records**: 1250
Your dataset contains 1250 rows of data.

---

**Q:** "What are the unique regions?"
**A:** 📊 **Unique values in 'region'**:
• Count: 5
• Samples: North America, Europe, Asia, Australia, South America

---

**Q:** "Average salary?"
**A:** 📊 **Average salary**: 55000.50
This is the mean value across all records.

## Pro Tips

1. **Be specific** - Mention the column name when possible
   - "What is the max salary?" (better)
   - "What is the max?" (works but less specific)

2. **Use natural language** - Questions can be casual
   - "What's the highest price?"
   - "Show me the minimum value"
   - "How many products?"

3. **Mix operations** - Combine queries
   - "Average sales by region?"
   - "Top 5 categories by revenue?"

## Troubleshooting

**Q: Why is my question not getting a direct answer?**
A: The system couldn't match your question format. It will fall back to:
   - LLM response (if credits available)
   - Context-based summary (if no credits)

**Q: Can I ask complex SQL-like queries?**
A: Currently supported are basic operations (max, min, avg, count, filter). Complex joins require LLM.

**Q: Do data retrieval questions use API credits?**
A: No! Direct data retrieval is 100% free and works offline.
