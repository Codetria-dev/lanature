export default function TaskItem({ routine, pet, isCompleted, isToggling, onToggle }) {
  return (
    <div
      className={`flex items-center gap-4 p-3 rounded-lg transition-colors ${
        isCompleted 
          ? 'bg-green-50/50' 
          : 'bg-white border border-gray-200'
      }`}
    >
      <input
        type="checkbox"
        checked={isCompleted}
        onChange={onToggle}
        disabled={isToggling}
        className="w-6 h-6 text-green-600 border-gray-300 rounded focus:ring-2 focus:ring-green-500 cursor-pointer disabled:opacity-50 flex-shrink-0"
      />
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${isCompleted ? 'line-through text-gray-400' : 'text-gray-900'}`}>
          {routine.type}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">
          {pet?.name} · {routine.time}
        </p>
      </div>
    </div>
  )
}
