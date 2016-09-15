import React, { Component, PropTypes } from 'react';
import classnames from 'classnames';

const Item = ({id, title, msg, theme, hideNotification}) => (
    <div className={classnames(styles.item, theme)} onClick={() => hideNotification(id)}>
        <p className={styles.title}>{title}</p>
        <p>{msg}</p>
    </div>
);

export default class Notify extends Component {
    key = 0;
    state = {};
    
    success(title, msg, time) {
        this.addNotify(title, msg, time, styles.success);
    }
    
    info(title, msg, time) {
        this.addNotify(title, msg, time, styles.info);
    }

    error(title, msg, time) {
        this.addNotify(title, msg, time, styles.error);
    }

    addNotify(title, msg, time, theme) {
        const key = this.key++;
        this.state[key] = { title, msg, time, theme };
        this.setState(this.state);
        this.countToHide(time, key);
    }
    
    countToHide(duration, key) {
        const that = this;
        setTimeout(() => {
            that.hideNotification(key);
        }, duration);
    }
    
    hideNotification(key) {
        console.log('hide: ', key);
        delete this.state[key];
        this.setState(this.state);
    }
    
    render() {
        const keys = Object.keys(this.state);
        return (
          <div className={styles.container}>
            {keys.map((key) =>
              <Item id={key} key={key} hideNotification={::this.hideNotification} {...this.state[key]} />
            )}    
          </div>  
        );
    }
}