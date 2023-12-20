import numpy as np

from scipy.stats import norm


class ProbabilityDefeat:
    def __init__(self):
        self.distance: float = 30

    def get_probit_overpressure_mix(self):
        pass

    def calculate_fatality_probability(self, probit_value, normal_distribution_mean=5):
        """
        Calculate probability of fatality from probit value

        Parameters
        ----------
        probit_value : float
            Value from probit model
        normal_distribution_mean : int
            Default value of 5 avoids negative values, consistent with published models

        Returns
        -------
        prob : float
            Probability of fatality

        """
        return norm.cdf(probit_value, loc=normal_distribution_mean)

    """
    THERMAL Fatality Probit Models
    """

    def compute_thermal_fatality_prob(self, model_ref, heat_flux, exposure_time, mean=5):
        """
        Calculate probability of fatality from thermal source using user-specified model

        Parameters
        ----------
        model_ref : str
            reference to internal thermal probit model function to apply (see below)
        heat_flux : float
            heat flux intensity (W/m^2)
        exposure_time : float
            duration of exposure (s)
        mean : int
            Default value of 5 avoids negative values, consistent with published models

        Returns
        -------
        prob : float
            Probability of fatality
        """
        cleaned_id = parse_thermal_model(model_ref)
        probit_model = PROBIT_THERMAL_CHOICES[cleaned_id]

        thermal_dose = calculate_thermal_dose(heat_flux, exposure_time)
        if thermal_dose == 0:
            probit_value = -np.inf
        else:
            probit_value = probit_model(thermal_dose)

        return calculate_fatality_probability(probit_value, mean)

    def calculate_thermal_dose(self, heat_flux, exposure_time):
        """
        Compute thermal dose for given time

        Parameters
        -------------
        heat_flux : float
            heat flux intensity (W/m^2)
        exposure_time : float
            duration of exposure (s)

        Returns
        ---------
        thermal_dose : float
            Thermal dose in (W/m^2)^4/3 s
        """
        return exposure_time * heat_flux ** (4/3)

    def thermal_eisenberg(self, thermal_dose):
        """
        Eisenberg - thermal exposure

        Parameters
        -------------
        thermal_dose : float
            Thermal dose in (W/m^2)^4/3 s

        Returns
        ---------
        probit_value : float
        """
        return -38.48 + 2.56 * np.log(thermal_dose)

    def thermal_tsao_perry(self, thermal_dose):
        """
        Tsao & Perry - thermal exposure

        Parameters
        -------------
        thermal_dose : float
            Thermal dose in (W/m^2)^4/3 s

        Returns
        ---------
        probit_value : float
        """
        return -36.38 + 2.56 * np.log(thermal_dose)

    def thermal_tno(self, thermal_dose):
        """
        TNO - thermal exposure

        Parameters
        -------------
        thermal_dose : float
            Thermal dose in (W/m^2)^4/3 s

        Returns
        ---------
        probit_value : float
        """
        return -37.23 + 2.56 * np.log(thermal_dose)

    def thermal_lees(self, thermal_dose):
        """
        Lees - thermal exposure

        Parameters
        -------------
        thermal_dose : float
            Thermal dose in (W/m^2)^4/3 s

        Returns
        ---------
        probit_value : float
        """
        return -29.02 + 1.99 * np.log(0.5 * thermal_dose)

    def thermal_pbtp(self):

        return -12.8 + 2.56 * np.log(thermal_dose)

    """
    OVERPRESSURE Fatality Probit Models

    TNO Lung hemorrhage requires the person's mass, so we don't calculate it

    TNO whole body impact model produces lower probabilities than head
    impact model, which means head impact fatalities will dominate whole
    body impact fatalities. So we don't include TNO whole body fatalities.
    """

    def compute_overpressure_fatality_prob(self, model_ref, overp, impulse=None, mean=5):
        """
        Calculate probability of fatality from overpressure using user-specified model

        Parameters
        ----------
        model_ref : str
            reference to internal probit model function to use (from available functions)
        overp : float
            Peak overpressure (Pa)
        impulse : float
            Impulse of shock wave (Pa*s)
            Not used in Eisenberg - Lung hemorrhage or HSE - Lung Hemorrhage models
        mean : int
            Default value of 5 avoids negative values, consistent with published models

        Returns
        -------
        prob : float
            Probability of fatality
        """
        cleaned_id = parse_overp_model(model_ref)
        probit_model = PROBIT_OVERP_CHOICES[cleaned_id]

        if overp == 0 or impulse == 0:
            probit_value = -np.inf
        else:
            if cleaned_id in ['leis', 'lhse']:
                probit_value = probit_model(overp=overp)
            else:
                probit_value = probit_model(overp=overp, impulse=impulse)

        return calculate_fatality_probability(probit_value, mean)

    def overp_eisenberg(self, overp):
        """
        Eisenberg - Lung hemorrhage

        Parameters
        ----------
        overp : float
            Peak overpressure (Pa)

        Returns
        -------
        probit_value : float
        """
        return -77.1 + 6.91 * np.log(overp)

    def overp_hse(self, overp):
        """
        HSE - Lung hemorrhage

        Parameters
        ----------
        overp : float
            Peak overpressure (Pa)

        Returns
        -------
        probit_value : float
        """
        return 5.13 + 1.37 * np.log(overp * 1e-5)

    def overp_tno_head(self, overp, impulse):
        """
        TNO - Head impact

        Parameters
        ----------
        overp : float
            Peak overpressure (Pa)
        impulse : float
            Impulse of shock wave (Pa*s)

        Returns
        -------
        probit_value : float
        """
        return 5 - 8.49 * np.log((2430 / overp) + 4.e8 / (overp * impulse))

    def overp_building_collapse(self, overp, impulse):
        """
        TNO - Structural (Building) collapse - Обрушение здания

        Parameters
        ----------
        overp : float
            Peak overpressure (Pa)
        impulse: impulse of shock wave (Pa*s)

        Returns
        -------
        probit_value : float
        """
        S = (40000 / overp) ** 7.4 + (460 / impulse) ** 11.3
        return 5 - 0.22 * np.log(S)

    def overp_major_structural_damage(self, overp, impulse):
        """
        Major Structural Damage - Серьезные структурные повреждения

        Parameters
        ----------
        overp : float
            Peak overpressure (Pa)
        impulse: impulse of shock wave (Pa*s)

        Returns
        -------
        probit_value : float
        """
        S = (40000 / overp) ** 7.4 + (460 / impulse) ** 11.3
        V = (17500 / overp) ** 8.4 + (290 / impulse) ** 9.3
        return 5 - 0.26 * np.log(V*S)

    def overp_minor_damages(self, overp, impulse):
        """
        Minor Damages - Незначительные повреждения здания

        Parameters
        ----------
        overp : float
            Peak overpressure (Pa)
        impulse: impulse of shock wave (Pa*s)

        Returns
        -------
        probit_value : float
        """
        S = (40000 / overp) ** 7.4 + (460 / impulse) ** 11.3
        V = (4600 / overp) ** 3.9 + (110 / impulse) ** 5.0
        return 5 - 0.26 * np.log(V*S)

    def overp_breakage_win_panes(self, overp):
        """
        Breakage of Window Panes - Разрушение оконных стекол

        Parameters
        ----------
        overp : float
            Peak overpressure (Pa)

        Returns
        -------
        probit_value : float
        """
        return -16.58 + 2.53 * np.log(overp * 1e-5)

    # Reference to fatality models
    #   key: internal reference string
    #   val: function reference
    PROBIT_THERMAL_CHOICES = {
        'eise': thermal_eisenberg,
        'tsao': thermal_tsao_perry,
        'tno': thermal_tno,
        'lees': thermal_lees,
    }

    # Reference to overpressure models
    #   key: internal reference string
    #   val: function reference
    # Note: keys are unique with above dict to ensure no accidental overlap
    PROBIT_OVERP_CHOICES = {
        'leis': overp_eisenberg,
        'lhse': overp_hse,
        'head': overp_tno_head,
        'coll': overp_tno_struct_collapse,
    }

    def parse_thermal_model(self, name):
        """ Determine model ID from string name """
        # parsed = re.sub(r'\W+', '', name.lower())
        cleaned = misc_utils.clean_name(name)  # alphanumeric lower-case

        if cleaned in ['eise', 'eisenberg', 'eis', 'eisen']:
            model_id = 'eise'
        elif cleaned in ['tsao', 'tsa']:
            model_id = 'tsao'
        elif cleaned in ['tno', 'tn']:
            model_id = 'tno'
        elif cleaned in ['lees', 'lee', 'le']:
            model_id = 'lees'
        else:
            raise ValueError(
                "Thermal model name {} not recognized".format(cleaned))

        return model_id

    def parse_overp_model(self, name):
        """ Determine model ID from string name """
        cleaned = misc_utils.clean_name(name)  # alphanumeric lower-case

        if cleaned in ['leis', 'lung_eisenberg', 'lungeisenberg', 'lunge', 'lung_eis', 'elh']:
            model_id = 'leis'
        elif cleaned in ['lhse', 'lung_hse', 'lunghse', 'lungh', 'lhs']:
            model_id = 'lhse'
        elif cleaned in ['head_impact', 'head', 'headimpact', 'hea']:
            model_id = 'head'
        elif cleaned in ['col', 'collapse', 'coll']:
            model_id = 'coll'
        else:
            raise ValueError(
                "Probit overpressure model name {} not recognized".format(cleaned))

        return model_id
