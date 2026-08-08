import React from 'react'
import "./About.css"
const About = () => {
  return (
    <div className="mainAbt">
        <div className="memberList">
            <div className="headerMembers">The Humans Behind It</div>
            <div className="members">
                <div>Panth Upadhyay</div>
                <div>Yash Raj Singh</div>
                <div>Nikhil Kumar Singh</div>
            </div>
        </div>
        <div className="RefDetails">
            <div className='information'>Information</div>
            <div>Background Image: Transmigration (Destiny 2)</div>
            <div>Design Inspiration: Hyprland (Arch Linux)</div>
            <div>Skillset: Vite-React, Gen Ai, Agentic Ai</div>
            <div>Languages: Python, Javascript, JavascriptReact</div>
        </div>
        <div className="extrInfo">
            <div className="extrTitle">External Links</div>
            <div className="extr">
                <div className="gitLink">
                    <div className="gitRef">Github:</div>
                    <div className="githubLink">github.com/xyz</div>
                </div>
            </div>
        </div>
    </div>
  )
}

export default About