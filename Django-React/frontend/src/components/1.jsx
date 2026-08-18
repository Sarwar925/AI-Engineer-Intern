import  { useState } from 'react'

const count = () => {
    const [count, setCount] = useState(0)
  return (
    <div>
      <button onClick=()=>{setCount= count+1}
      > </button>
    </div>
  )
}

export default count
