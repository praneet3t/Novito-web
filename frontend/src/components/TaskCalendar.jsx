import { useState, useEffect } from "react";

export default function TaskCalendar({ tasks }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    return { daysInMonth, startingDayOfWeek, year, month };
  };

  const getTasksForDate = (date) => {
    return tasks.filter(t => {
      if (!t.due_date) return false;
      const taskDate = new Date(t.due_date);
      return taskDate.toDateString() === date.toDateString();
    });
  };

  const { daysInMonth, startingDayOfWeek, year, month } = getDaysInMonth(currentDate);
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  const days = [];
  for (let i = 0; i < startingDayOfWeek; i++) {
    days.push(<div key={`empty-${i}`} className="calendar-day"></div>);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day);
    const tasksOnDay = getTasksForDate(date);
    const isToday = date.toDateString() === new Date().toDateString();
    const isWeekend = date.getDay() === 0 || date.getDay() === 6;

    days.push(
      <div
        key={day}
        className={`calendar-day ${isToday ? 'today' : ''} ${tasksOnDay.length > 0 ? 'has-tasks' : ''} ${isWeekend ? 'weekend' : ''}`}
        onClick={() => setSelectedDate(date)}
      >
        <span>{day}</span>
        {tasksOnDay.length > 0 && <span className="task-count">{tasksOnDay.length}</span>}
      </div>
    );
  }

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <button className="btn small secondary" onClick={prevMonth}>&lt;</button>
        <strong>{monthNames[month]} {year}</strong>
        <button className="btn small secondary" onClick={nextMonth}>&gt;</button>
      </div>

      <div className="calendar-grid">
        {dayNames.map(name => (
          <div key={name} style={{textAlign: 'center', fontWeight: 600, fontSize: '11px', padding: '4px', color: 'var(--text-secondary)'}}>
            {name}
          </div>
        ))}
        {days}
      </div>

      {selectedDate && (
        <div style={{marginTop: '16px', padding: '12px', background: 'var(--bg)', borderRadius: '4px'}}>
          <strong style={{fontSize: '13px'}}>{selectedDate.toDateString()}</strong>
          <div style={{marginTop: '8px'}}>
            {getTasksForDate(selectedDate).map(t => (
              <div key={t.id} className="chip" style={{display: 'block', marginTop: '4px'}}>
                {t.description}
              </div>
            ))}
            {getTasksForDate(selectedDate).length === 0 && (
              <div className="muted small">No tasks due</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
