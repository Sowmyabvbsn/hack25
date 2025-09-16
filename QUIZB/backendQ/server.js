require('dotenv').config(); // Load .env at top
const express = require('express');
const cors = require('cors');
const { OpenAI } = require('openai'); // Correct import!

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const app = express();
app.use(cors());
app.use(express.json());

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
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7,
    });

    const content = completion.choices[0].message.content.trim();

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
    if (!questions) return res.status(400).json({ error: "OpenAI gave unexpected response" });

    res.json({ questions });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Quiz generation failed" });
  }
});

const PORT = 4000;
app.listen(PORT, () => console.log(`Quiz backend running on port ${PORT}`));
