import React, { Component } from "react";
import PropTypes from "prop-types";
import shortid from "shortid";

const uuid = shortid.generate;

class SeriesList extends React.Component {
  constructor(props, context) {
    super(props, context);

    this.state = {
      data: [],
    };
  }

  componentDidMount() {
    fetch('api/series/')
      .then(response => response.json())
      .then((data) => { this.setState({ data });
     });
   }

   render() {
     if (!this.state.data) {
       <p>Nothing to show</p>
     }

     return (
       <div className="columns is-multiline">
         {this.state.data.map(el => (
           <div className="column is-one-fifth" key={uuid()}>
             <div className="card" key={uuid()}>
               <div className="card-header">
                 <p className="card-header-title is-centered" key={uuid()}>{el.name}</p>
               </div>
               <div className="card-image">
                 <figure className="image is-2by3">
                   <img src={el.image.image} alt="Placeholder image" key={uuid()}></img>
                 </figure>
               </div>
               <footer className="card-footer">
                 <p className="card-footer-item">
                   <span key={uuid()}>{el.issue_count} Books</span>
                 </p>
                 <a href="#" className="card-footer-item" key={uuid()}>Open Series</a>
               </footer>
             </div>
           </div>
         ))}
       </div>
     );
   }
 }

export default SeriesList;
