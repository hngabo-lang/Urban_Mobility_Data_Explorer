const filters = {
 form: document.getElementById("filter-form"),
 
 fillHours() {
    const select = document.getElementById("filter-hour");
    
    for (let hour =0; hour < 24; hour++) {
        const label = `${String(hour).padStart(2,"0")}:00`;
        select.add(new Option(label, hour));
            }
 
},

// borough dropdown, suing the list from /api/boroughs

fillBoroughs(boroughs) {
    const select = document.getElementById("filter-borough");

    boroughs.forEach((borough) => {
        select.add(
            new Option(borough.borough_name, borough.borough_name)
        );
    });
    },

    // turn the form into API parameters, skipping empty fields
    //each input's name matches a parameter in backend/api/trips.py
    read(){
        const params = {};
            for(const [name, value] of new FormData(this.form)){
                if (value !== "") {
                    params[name] = value;
                }
            }
        return params;
        
    },

    // make sure "min" is not bigger than "max" before calling the API
    checkRanges(){
        const pairs = [
            [
                "start_date",
                "end_date",
                "'To date' can't be before 'from date'", 
                false
            ],
            [  
                "min_distance",
                "max_distance",
                "max distance can't be below",
                true
                ],
                ["min_fare",
                 "max_fare",
                 "max fare can't be below min",
                 true
                ],
            ];
              
                for (const [minName, maxName, message, isNumber] of pairs){
                    const minInput = this.form.elements[minName];
                    const maxInput = this.form.elements[maxName];
                        
                    maxInput.setCustomValidity("");
                        
                        if(minInput.value !== "" && maxInput.value !== "") {
                          const min = isNumber
                          ? Number(minInput.value)
                          : minInput.value;
                           const max = isNumber 
                           ? Number(maxInput.value)
                           : maxInput.value;
                            
                          if(max < min) {
                                    maxInput.setCustomValidity(message);
                                }
                            }

                                }
                           // shows the browser's own error bubble on the first bad field
                           return this.form.reportValidity();
                            },
                            //call "callback" with new parameters whenever Apply or reset is clicked
                            onChange(callback) {
                                this.form.addEventListener("submit",(event) => {
                                    event.preventDefault(); //stop the page from reloading
                                    
                                    if(this.checkRanges()){
                                        callback(this.read());
    
                                    }
                                });
                                this.form.addEventListener("reset", () => {
                                    //the browser clears the fields just AFTER this event, so wait a moment
                                    setTimeout(() => {
                                        for(const input of this.form.elements) {
                                            if(input.setCustomValidity) {
                                                input.setCustomValidity("");
                                        }
                                    }
                                    
                                   callback({});
                                    }, 0);

                            });
                                },
                            };   
         
