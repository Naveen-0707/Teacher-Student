import React from 'react';

const TeacherView = ({ answers }) => {
  return (
    <div>
      <h2>Teacher View</h2>
      <table>
        <thead>
          <tr>
            <th>Question</th>
            <th>Answer</th>
          </tr>
        </thead>
        <tbody>
          {answers.map((a, i) => (
            <tr key={i}>
              <td>{a.question}</td>
              <td>{a.answer}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TeacherView;
