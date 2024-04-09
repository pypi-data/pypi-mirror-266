/**
 * Патч над стандартным компонентом ГАР.
 * Перекрыт метод выбора населенного пункта
 * ввиду наличия населенных пунктов без улиц,
 * но имеющих привязанные дома
 * Блокируем и снимаем обязательность с поля выбора улицы
 * для таких населенных пунктов
 */

var originalOnPlaceChange = Ext.m3.gar.AddressFields.prototype.onPlaceSelect;

Ext.override(Ext.m3.gar.AddressFields, {
    onPlaceSelect: function(field, newValue, oldValue) {
        var record;

        if (this.streetNameField) {
            record = this.placeNameField.store.getAt(
                this.placeNameField.selectedIndex);

            if (record && 'hasChildren' in record.json) {
                this.streetNameField.setDisabled(!record.json['hasChildren']);
            }

            this.streetNameField.validate();
        }

        originalOnPlaceChange.apply(this, [field, newValue, oldValue]);
    },
    // функция построения полного адреса, с учетом необязательности улиц
    getFullAddress: function() {
        var addressParts = [];

        if (!this.isZipCodeEmpty()) {
            addressParts.push(this.zipCodeField.getValue());
        }

        if (!this.isPlaceEmpty()) {
            addressParts.push(this.placeNameField.getValue());

            if (this.hasStreetField() && !this.isStreetEmpty()) {
                addressParts.push(this.streetNameField.getValue());
            }
            // если улица допускается пустой, то отображаем дома
            if (this.hasStreetField() && (!this.isStreetEmpty() ||
                  (this.isStreetEmpty() && this.streetNameField.allowBlank))) {
                if (this.hasHouseField() && !this.isHouseEmpty()) {
                    if (this.houseNumberField.getValue().indexOf('уч.') > -1) {
                        addressParts.push(
                            'земельный участок ' + this.houseNumberField.getValue().substring(4)
                        );
                    }
                    else {
                        addressParts.push(
                            this.houseTypeField.getValue() + this.houseNumberField.getValue()
                        );
                    }
                }

                if (this.hasHouseField() && !this.isBuildingEmpty()) {
                    addressParts.push(
                        this.buildingTypeField.getValue() + this.buildingNumberField.getValue()
                    );
                }

                if (this.hasHouseField() && !this.isStructureEmpty()) {
                    addressParts.push(
                        this.structureTypeField.getValue() + this.structureNumberField.getValue()
                    );
                }

                if (this.hasFlatField() && !this.isFlatEmpty()) {
                    addressParts.push(
                        'кв.' + this.flatNumberField.getValue()
                    );
                }
            }
        }

        return addressParts.join(', ');
    },
    isHouseEmpty: function() {
        return (
            !this.houseNumberField.getValue() &&
            !this.buildingNumberField.getValue() &&
            !this.structureNumberField.getValue() &&
            !this.houseTypeField.getValue()
        );
    }
});

Ext.m3.gar.NewAddressView = Ext.extend(Ext.m3.gar.RowsAddressView, {

    initRow2: function() {
        var rowItems = [];

        if (this.fields.streetNameField) {
            this.addStreetField(rowItems);
        }

        if (rowItems.length > 0) {
            this.setPaddings(rowItems);

            this.row2 = new Ext.Container({
                items: rowItems,
                layout: 'hbox',
                layoutConfig: {
                    'align': 'middle'
                }
            });
            this.add(this.row2);
        }
    },

    initRow4: function() {
        var rowItems = [];

        if (this.fields.houseNumberField) {
            this.addHouseField(rowItems);
        }
        if (this.fields.flatNumberField) {
            this.addFlatField(rowItems);
        }

        if (rowItems.length > 0) {
            this.setPaddings(rowItems);

            this.row4 = new Ext.Container({
                items: rowItems,
                layout: 'hbox'
            });
            this.add(this.row4);
        }
    },

    addHouseField: function(rowItems) {
        this.houseFieldContainer = this.formed(
            this.fields.houseNumberField,
            this.labelsWidth.house,
            {
                'flex': 1.5
            }
        );
        this.buildingFieldContainer = this.formed(
            this.fields.buildingNumberField,
            this.labelsWidth.building,
            {
                'flex': 2
            }
        );
        this.structureFieldContainer = this.formed(
            this.fields.structureNumberField,
            this.labelsWidth.structure,
            {
                'flex': 1
            }
        );
        rowItems.push(
            this.houseFieldContainer,
            this.buildingFieldContainer,
            this.structureFieldContainer,
            this.fields.houseIDField,
            this.fields.houseTypeField,
            this.fields.buildingTypeField,
            this.fields.structureTypeField
        );
    },

    addFlatField: function(rowItems) {
        this.flatFieldContainer = this.formed(
            this.fields.flatNumberField,
            this.labelsWidth.flat,
            {
                'flex': 1
            }
        );
        rowItems.push(
            this.flatFieldContainer
        );
    },

    initComponent: function() {
        Ext.m3.gar.RowsAddressView.superclass.initComponent.call(this);

        this.initRow1();
        this.initRow2();
        this.initRow4();
        // Переносим 3-й ряд на 4-й, т.к.
        // часть полей из 2-го ряда вынесли в отдельный
        this.initRow3();

        if (this.fields.hasStreetField()) {
            this.mon(
                this.fields.streetNameField.getStore(),
                'load',
                this.onStreetLoad,
                this
            )
        }
    }
});
