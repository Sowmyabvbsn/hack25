require('dotenv').config(); // Load .env at top
const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const app = express();
app.use(cors());
app.use(express.json());

// Add a health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Quiz backend is running' });
});

app.post('/quiz', async (req, res) => {
  const { ageGroup } = req.body;

  let prompt = "";
  if (ageGroup === "kids") {
    prompt = "Generate a JSON array of 5 simple Indian heritage MCQ quiz questions for children below age 15. Each object must have 'q' (question), 'options' (array of 4), and 'answer' (index of correct option).";
  } else if (ageGroup === "teens") {
    prompt = "Generate a JSON array of 5 moderately difficult Indian heritage MCQ quiz questions for teenagers age 15-19. Each object must have 'q' (question), 'options' (array of 4), and 'answer' (index of correct option).";
  } else {
    prompt = "Generate a JSON array of 5 challenging Indian heritage MCQ quiz questions for adults age 20 and above. Each object must have 'q' (question), 'options' (array of 4), and 'answer' (index of correct option).";
  }

  try {
    const result = await model.generateContent({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 2048,
      },
    });

    const content = result.response.text().trim();

    let questions = null;
    try {
      questions = JSON.parse(content);
    } catch (e) {
      // Try to extract JSON array if not pure JSON
      const firstBracket = content.indexOf("[");
      const lastBracket = content.lastIndexOf("]");
      if (firstBracket !== -1 && lastBracket !== -1) {
        questions = JSON.parse(content.substring(firstBracket, lastBracket + 1));
      }
    }
    if (!questions) return res.status(400).json({ error: "Gemini gave unexpected response" });

    res.json({ questions });
  } catch (error) {
    console.error(error);
    
    // Handle different types of errors
    if (error.code === 'ENOTFOUND' || error.message.includes('timeout')) {
      res.status(503).json({ 
        error: "Gemini service temporarily unavailable. Please try again later.",
        fallback: true 
      });
    } else if (error.status === 401) {
      res.status(401).json({ error: "Invalid Gemini API key" });
    } else {
      res.status(500).json({ error: "Quiz generation failed. Please try again." });
    }
  }
});

const PORT = 4000;
app.listen(PORT, () => console.log(`Quiz backend running on port ${PORT}`));
