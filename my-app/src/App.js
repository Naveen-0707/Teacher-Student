import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

const Teacher = () => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [currentAnswer, setCurrentAnswer] = useState("");

  useEffect(() => {
    const questionList = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key.startsWith("answer_")) {
        questionList.push(key);
      }
    }
    setQuestions(questionList);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem(currentQuestion, currentAnswer);
    setCurrentQuestion("");
    setCurrentAnswer("");
    setQuestions([...questions, currentQuestion]);
  };

  return (
    <div>
      <h2>Teacher Page</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Question:
          <input
            type="text"
            value={currentQuestion}
            onChange={(e) => setCurrentQuestion(e.target.value)}
          />
        </label>
        <br />
        <label>
          Answer:
          <input
            type="text"
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
          />
        </label>
        <br />
        <button type="submit">Add</button>
      </form>
      <hr />
      <h3>Questions:</h3>
      <ul>
        {questions.map((question) => {
          const answer = localStorage.getItem(question);
          return (
            <li key={question}>
              {question}: {answer}
            </li>
          );
        })}
      </ul>
    </div>
  );
};

const Student = () => {
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    const questionList = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key.startsWith("answer_")) {
        questionList.push(key);
      }
    }
    setQuestions(questionList);
  }, []);

  const handleSubmit = (e, question) => {
    e.preventDefault();
    const answer = e.target.elements.answer.value;
    localStorage.setItem(`answer_${question}`, answer);
    alert(`Your answer for "${question}" has been submitted.`);
  };

  return (
    <div>
      <h2>Student Page</h2>
      <h3>Questions:</h3>
      <ul>
        {questions.map((question) => {
          const answer = localStorage.getItem(`answer_${question}`);
          return (
            <li key={question}>
              {question}
              <form onSubmit={(e) => handleSubmit(e, question)}>
                <input type="text" name="answer" defaultValue={answer} />
                <button type="submit">Submit</button>
              </form>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Teacher</Link>
            </li>
            <li>
              <Link to="/student">Student</Link>
            </li>
          </ul>
        </nav>
        <Switch>
          <Route path="/student">
            <Student />
          </Route>
          <Route path="/">
            <Teacher />
          </Route>
        </Switch>
      </div>
    </Router>)}
 
 export default App;