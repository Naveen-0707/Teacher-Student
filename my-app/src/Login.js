import React, { useState } from 'react';
import TeacherView from './TeacherView';
import StudentView from './StudentView';

const Login = ({ username, password }) => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [isTeacher, setIsTeacher] = useState(false);
  const [answers, setAnswers] = useState([]);

  const handleLogin = () => {
    if (username === 'teacher' && password === 'teacher123') {
      setIsTeacher(true);
      setLoggedIn(true);
      setAnswers([
        { question: "seven(times(five()))", answer: "35" },
        { question: "four(plus(nine()))", answer: "13" },
        { question: "eight(minus(three()))", answer: "5" },
        { question: "six(divided_by(two()))", answer: "3" },
      ]);
    } else if (username === 'student' && password === 'student123') {
      setIsTeacher(false);
      setLoggedIn(true);
    } else {
      alert('Invalid username or password');
    }
  }

  const handleSubmit = (submittedAnswers) => {
    setAnswers(submittedAnswers);
    alert('Answers submitted!');
  }

  if (!loggedIn) {
    return null;
  }

  return (
    <div>
      <button onClick={handleLogin}>Login</button>
      {isTeacher ? (
        <TeacherView answers={answers} />
      ) : (
        <StudentView
          questions={[
            "seven(times(five()))",
            "four(plus(nine()))",
            "eight(minus(three()))",
            "six(divided_by(two()))",
          ]}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
};

export default Login;
