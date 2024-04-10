from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from djangoldp.models import Model
from djangoldp_conversation.models import Conversation, Message
from djangoldp_community.models import Community, CommunityMember
from djangoldp.permissions import LDPBasePermission, AnonymousReadOnly, ReadOnly, ReadAndCreate, ACLPermissions, OwnerPermissions, InheritPermissions
from djangoldp_tzcld.permissions import RegionalReferentPermissions

Community._meta.nested_fields += ['tzcld_community_requests', 'community_answer', 'tzcld_community_followed_answer']
Community._meta.permission_classes = [AnonymousReadOnly, ReadAndCreate|ACLPermissions|RegionalReferentPermissions]

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Députés => Circonscription
#############################
class TzcldTerritoryCirconscription(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    order = models.IntegerField(blank=True, null=True, default=1)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Circonscription')
        verbose_name_plural = _("TZCLD Options Circonscriptions")

        container_path = "tzcld-circonscriptions/"
        serializer_fields = ['@id', 'name', 'order']
        ordering = ['order']
        nested_fields = []
        rdf_type = "tzcld:circonscriptions"
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['territories_deputies_circonscriptions']


#############################
# Page d'edition du territoire => Départements
# Page Etat d'avancement => Carte d’identité du territoire => Sénateurs => Département
# Page d'edition de  l'utilisateur => Départements
# Page d'edition de  l'utilisateur => Postes => Département
#############################
class TzcldTerritoryDepartment(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Department')
        verbose_name_plural = _("TZCLD Options Departments")

        container_path = "tzcld-departments/"
        serializer_fields = ['@id', 'name', 'job_department']
        ordering = ['name']
        nested_fields = []
        rdf_type = "tzcld:departments"
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['territories_senators_departments', 'community_departments', 'job_department', 'profile_department']


#############################
# Page d'edition du territoire => Régions
# Page d'edition de  l'utilisateur => Régions
#############################
class TzcldTerritoryRegion(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    referents = models.ManyToManyField(get_user_model(), related_name='regions', blank=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Région')
        verbose_name_plural = _("TZCLD Régions")

        container_path = "tzcld-regions/"
        serializer_fields = ['@id', 'name', 'referents']
        ordering = ['name']
        nested_fields = ['referents']
        rdf_type = "tzcld:regions"
        permission_classes=[ReadAndCreate|InheritPermissions]
        inherit_permissions = ['community_regions', 'profile_regions']

#############################
# Page d'edition du territoire => Type d'organisation
#############################
class TzcldProfilesMembership(Model):
    name = models.CharField(max_length=255, blank=False, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Membership type')
        verbose_name_plural = _("TZCLD Options Membership types")

        container_path = "tzcld-profile-membership/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:profileMembership"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['community']


#############################
# Page d'edition de  l'utilisateur => Etant le modèle User
#############################
class TzcldProfile(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tzcld_profile")
    last_contribution_year = models.CharField(max_length=255, blank=True, null=True, default='')
    regions = models.ManyToManyField(TzcldTerritoryRegion, related_name='profile_regions', blank=True)
    departments = models.ManyToManyField(TzcldTerritoryDepartment, related_name='profile_department', blank=True)
    is_member = models.BooleanField(default=False)
    is_national_referent = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} ({})'.format(self.user.get_full_name(), self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD User Profile')
        verbose_name_plural = _("TZCLD Users Profiles")

        ordering = ['user']
        serializer_fields = ['@id', 'last_contribution_year', 'jobs', 'regions', 'departments', 'is_member', 'is_national_referent']
        rdf_type = "tzcld:profile"
        auto_author = 'user'
        depth = 1
        nested_fields = ['jobs', 'regions', 'departments']
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['user']


#############################
# Page d'edition de l'utilisateur => Postes
#############################
class TzcldProfileJob(Model):
    position = models.CharField(max_length=255, blank=True, null=True, default='')
    organisation = models.CharField(max_length=255, blank=True, null=True, default='')
    address = models.CharField(max_length=255, blank=True, null=True, default='')
    postal_code = models.CharField(max_length=255, blank=True, null=True, default='')
    city = models.CharField(max_length=255, blank=True, null=True, default='')
    department = models.ForeignKey(TzcldTerritoryDepartment, on_delete=models.DO_NOTHING,related_name='job_department', blank=True, null=True)
    #address_public = models.BooleanField(default=False)
    profile = models.ForeignKey(TzcldProfile, on_delete=models.CASCADE,related_name='jobs', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True, default='')

    phone = models.CharField(max_length=255, blank=True, null=True, default='')
    phone_public = models.BooleanField(default=False)
    mobile_phone = models.CharField(max_length=255, blank=True, null=True, default='')
    mobile_phone_public = models.BooleanField(default=False)
    email = models.CharField(max_length=255, blank=True, null=True, default='')
    email_public = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} ({})'.format(self.position, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD User profile job')
        verbose_name_plural = _("TZCLD Users profiles jobs")

        container_path = "tzcld-profile-job/"
        serializer_fields = ['@id', 'position', 'organisation', 'address', 'postal_code', 'city', 'department','profile', 'link','phone' ,'phone_public' ,'mobile_phone' ,'mobile_phone_public' ,'email' ,'email_public' ]
        nested_fields = []
        rdf_type = "tzcld:profileJob"
        permission_classes=[ReadOnly|OwnerPermissions]


#############################
# Page d'edition du territoire => Etat d'avancement
#############################
class TzcldTerritoriesStepState(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory step state')
        verbose_name_plural = _("TZCLD Options Territories step states")

        container_path = "tzcld-territories-step-states/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:territoryStepState"
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['step_state']

#############################
# Page d'edition du territoire => Type de territoire
#############################
class TzcldTerritoriesKind(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Kind')
        verbose_name_plural = _("TZCLD Options Territories Kind")

        container_path = "tzcld-kinds/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:territoryKind"
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['kind']

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Origine de la mobilisation
#############################
class TzcldTerritoriesOriginMobilization(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Origin Mobilization')
        verbose_name_plural = _("TZCLD Options Origins Mobilization")

        container_path = "tzcld-origins-mobilization/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:territoryOriginMobilization"
        permission_classes=[ReadOnly]


#############################
# Page Etat d'avancement => Carte d’identité du territoire => Participation aux formations TZCLD => Formation suivie
#############################
class TzcldTerritoriesTrainingCourse(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Training Course')
        verbose_name_plural = _("TZCLD Options Training Courses")

        container_path = "tzcld-training-courses/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:territoryTrainingCourse"
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['territory_training_course']

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Participation aux formations TZCLD => Numéro de promotion
#############################
class TzcldTerritoriesTrainingPromotion(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Training Promotion')
        verbose_name_plural = _("TZCLD Options Training Promotions")

        container_path = "tzcld-training-promotions/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:territoryTrainingPromotion"
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['territory_training_promotion']

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Equipe projet => Statut de la personne
#############################
class TzcldTerritoriesTeamUserState(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    order = models.IntegerField(blank=True, null=True, default=1)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Team User State')
        verbose_name_plural = _("TZCLD Options Team User States")

        ordering = ['order']
        container_path = "tzcld-team-user-states/"
        serializer_fields = ['@id', 'name', 'order']
        nested_fields = []
        rdf_type = "tzcld:territoryTeamUserState"
        permission_classes=[ReadOnly|InheritPermissions]
        inherit_permissions = ['team_member_state']


#############################
# Page d'edition du territoire => Etant le modèle Community
#############################
class TzcldCommunity(Model):
    community = models.OneToOneField(Community, on_delete=models.CASCADE, related_name='tzcld_profile', null=True, blank=True)
    kind = models.ForeignKey(TzcldTerritoriesKind, on_delete=models.DO_NOTHING,related_name='kind', blank=True, null=True)
    step_state = models.ForeignKey(TzcldTerritoriesStepState, on_delete=models.DO_NOTHING,related_name='step_state', blank=False, null=True)
    regions = models.ManyToManyField(TzcldTerritoryRegion, related_name='community_regions', blank=True)
    departments = models.ManyToManyField(TzcldTerritoryDepartment, related_name='community_departments', blank=True)
    membership = models.ForeignKey(TzcldProfilesMembership, on_delete=models.DO_NOTHING,related_name='community', blank=False, null=True)
    membership_organisation_name = models.CharField(max_length=254, blank=True, null=True, default='')
    visible = models.BooleanField(default=True)
    primary_contact = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='primary_contact', blank=True, null=True, on_delete=models.SET_NULL)
    information = models.TextField(blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Profile')
        verbose_name_plural = _("TZCLD Territories Profiles")

        ordering = ['community']
        container_path = "tzcld-communities/"
        serializer_fields = ['@id', 'community', 'kind', 'step_state', 'kind', 'departments', 'regions', 'locations', 'primary_contact', 'membership', 'membership_organisation_name', 'visible', 'information']
        rdf_type = "tzcld:communityProfile"
        nested_fields = ['regions', 'departments', 'locations']
        permission_classes=[InheritPermissions]
        inherit_permissions = ['community']
        community_path = 'community'
        depth = 1

#############################
# Page Etat d'avancement => Carte d’identité du territoire
#############################
class TzcldCommunityIdentity(Model):
    community = models.OneToOneField(Community, on_delete=models.CASCADE, related_name='tzcld_profile_identity', null=True, blank=True)
    origin_mobilization = models.ForeignKey(TzcldTerritoriesOriginMobilization, on_delete=models.DO_NOTHING,related_name='territory_origin_mobilization', blank=True, null=True)
    application_date =  models.DateField(verbose_name="Estimated application date", blank=True, null=True)
    signatory_structure = models.CharField(max_length=254, blank=True, null=True, default='')
    birth_date =  models.IntegerField(verbose_name="Project birth year", blank=True, null=True)
    last_contribution_date =  models.DateField(verbose_name="Last contribution date", blank=True, null=True)
    conversations = models.ManyToManyField(Conversation, blank=True, related_name='tzcld_community_identity')
    date =  models.DateField(verbose_name="Date", auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    emergence_date =  models.DateField(verbose_name="Date of recognition of project emergence", blank=True, null=True)
    habilitation_date =  models.DateField(verbose_name="Date of habilitation", blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        auto_author = 'author'
        verbose_name = _('TZCLD Territory Identity')
        verbose_name_plural = _("TZCLD Territories Identities")
        ordering = ['community']
        container_path = "tzcld-communities-identity/"
        serializer_fields = ['@id', 'community', 'emergence_date', 'habilitation_date', 'origin_mobilization', 'application_date', 'signatory_structure', 'birth_date', 'last_contribution_date', 'territories_project_team_members', 'territories_trainings', 'conversations', 'tzcld_admins_community_shared_notes', 'tzcld_admins_community_shared_files', 'date', 'author', 'territories_political_landscape_deputies', 'territories_political_landscape_senators']
        nested_fields = ['community', 'conversations', 'tzcld_admins_community_shared_notes', 'tzcld_admins_community_shared_files', 'territories_project_team_members', 'territories_trainings', 'territories_political_landscape_deputies', 'territories_political_landscape_senators']
        rdf_type = "tzcld:communityIdentity"
        permission_classes=[InheritPermissions|RegionalReferentPermissions]
        inherit_permissions = ['community']
        community_path = 'community'
        depth = 1


#############################
# Page d'edition du territoire => Coordonnées et lieux (alias EBE)
#############################
class TzcldTerritoryLocation(Model):
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    address = models.CharField(max_length=255, blank=True, null=True, default='')
    postal_code = models.CharField(max_length=255, blank=True, null=True, default='')
    city = models.CharField(max_length=255, blank=True, null=True, default='')
    community = models.ForeignKey(TzcldCommunity, on_delete=models.CASCADE,related_name='locations', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory location')
        verbose_name_plural = _("TZCLD Territories locations")

        container_path = "tzcld-territories-location/"
        serializer_fields = ['@id', 'name', 'address', 'postal_code', 'city', 'phones', 'emails', 'community']
        nested_fields = ['emails', 'phones']
        rdf_type = "tzcld:territoryLocation"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['community']

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Equipe projet
#############################
class TzcldTerritoryProjectTeamMember(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    user_state = models.ForeignKey(TzcldTerritoriesTeamUserState, on_delete=models.DO_NOTHING,related_name='team_member_state', blank=True, null=True)
    etp = models.CharField(max_length=255, blank=True, null=True, default='')
    attachment_structure = models.CharField(max_length=255, blank=True, null=True, default='')
    community_identity = models.ForeignKey(TzcldCommunityIdentity, on_delete=models.CASCADE,related_name='territories_project_team_members', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.community_identity.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Project Team Member')
        verbose_name_plural = _("TZCLD Territories Project Team Members")

        container_path = "tzcld-territories-project-team-member/"
        serializer_fields = ['@id', 'user', 'user_state', 'etp', 'attachment_structure', 'community_identity']
        nested_fields = ['community_identity']
        rdf_type = "tzcld:territoryProjectTeamMember"
        permission_classes=[InheritPermissions|RegionalReferentPermissions]
        inherit_permissions = ['community_identity']
        community_path = 'community_identity.community'

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Paysage politique / institutionnel : Député-e 
#############################
class TzcldTerritoryPoliticalLandscapeDeputy(Model):
    deputy = models.CharField(max_length=254, blank=True, null=True, default='')
    circonscription = models.ForeignKey(TzcldTerritoryCirconscription, on_delete=models.DO_NOTHING,related_name='territories_deputies_circonscriptions', blank=True, null=True)
    community_identity = models.ForeignKey(TzcldCommunityIdentity, on_delete=models.CASCADE,related_name='territories_political_landscape_deputies', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.community_identity.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Political Landscape Deputy')
        verbose_name_plural = _("TZCLD Territories Political Landscape Deputies")

        container_path = "tzcld-territories-political-landscape-deputy/"
        serializer_fields = ['@id', 'deputy', 'circonscription', 'community_identity']
        nested_fields = ['community_identity']
        rdf_type = "tzcld:territoryPoliticalLandscapeDeputy"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['community_identity']

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Paysage politique / institutionnel : Sénateur-ice  
#############################
class TzcldTerritoryPoliticalLandscapeSenator(Model):
    senator = models.CharField(max_length=254, blank=True, null=True, default='')
    circonscription = models.ForeignKey(TzcldTerritoryDepartment, on_delete=models.DO_NOTHING,related_name='territories_senators_departments', blank=True, null=True)
    community_identity = models.ForeignKey(TzcldCommunityIdentity, on_delete=models.CASCADE,related_name='territories_political_landscape_senators', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.community_identity.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Political Landscape Senator')
        verbose_name_plural = _("TZCLD Territories Political Landscape Senators")

        container_path = "tzcld-territories-political-landscape-senator/"
        serializer_fields = ['@id', 'senator', 'circonscription', 'community_identity']
        nested_fields = ['community_identity']
        rdf_type = "tzcld:territoryPoliticalLandscapeSenator"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['community_identity']

#############################
# Page Etat d'avancement => Carte d’identité du territoire => Participation aux formations TZCLD 
#############################
class TzcldTerritoryTraining(Model):
    training_course = models.ForeignKey(TzcldTerritoriesTrainingCourse, on_delete=models.DO_NOTHING,related_name='territory_training_course', blank=True, null=True)
    training_promotion = models.ForeignKey(TzcldTerritoriesTrainingPromotion, on_delete=models.DO_NOTHING,related_name='territory_training_promotion', blank=True, null=True)
    training_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    community_identity = models.ForeignKey(TzcldCommunityIdentity, on_delete=models.CASCADE,related_name='territories_trainings', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.community_identity.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Training')
        verbose_name_plural = _("TZCLD Territories Trainings")

        container_path = "tzcld-territories-training/"
        serializer_fields = ['@id', 'training_course', 'training_promotion', 'training_person', 'community_identity']
        nested_fields = ['community_identity']
        rdf_type = "tzcld:territoryTraining"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['community_identity']


#############################
# Page Etat d'avancement => Auto-evaluation => Parties (pointsParts) => Points => Réponses => valeur de la réponse
#############################
class TzcldCommunityDeliberation(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory deliberation')
        verbose_name_plural = _("TZCLD Options Territories deliberations")

        container_path = "tzcld-communities-deliberations/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:communityDeliberation"
        permission_classes=[ReadOnly|OwnerPermissions]

#############################
# Page Etat d'avancement => Auto-evaluation => Parties (pointsParts) => Points => Réponses => valeur de la réponse
#############################
class TzcldOtherCommunityDeliberation(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Other Territory deliberation')
        verbose_name_plural = _("TZCLD Options Other Community deliberations")

        container_path = "tzcld-others-communities-deliberations/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:otherCommunityDeliberation"
        permission_classes=[ReadOnly|OwnerPermissions]


#############################
# Page Etat d'avancement => Auto-evaluation => Parties (pointsParts) => Points => Réponses => valeur de la réponse
#############################
class TzcldCouncilDepartmentDeliberation(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Council department deliberation')
        verbose_name_plural = _("TZCLD Options Council department deliberations")

        container_path = "tzcld-councils-departments-deliberations/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:councilDepartmentDeliberation"
        permission_classes=[ReadOnly|OwnerPermissions]

#############################
# Page Etat d'avancement => Auto-evaluation => Partie
#############################
class TzcldCommunityEvaluationPointPart(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    title = models.CharField(max_length=254, blank=True, null=True, default='')
    subtitle = models.CharField(max_length=254, blank=True, null=True, default='')
    order = models.IntegerField(blank=True, null=True, default=1)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Evaluation Point Part')
        verbose_name_plural = _("TZCLD Territories Evaluation Point Parts")

        container_path = "tzcld-evaluation-point-parts/"
        serializer_fields = ['@id', 'name', 'title', 'subtitle', 'order', 'part_points']
        ordering = ['order']
        nested_fields = ['part_points']
        rdf_type = "tzcld:evaluationPointPart"
        permission_classes=[ReadOnly|OwnerPermissions]
        depth = 0

#############################
# Page Etat d'avancement => Auto-evaluation => Parties (pointsParts) => Point
#############################
class TzcldCommunityEvaluationPoint(Model):
    TYPE_FALSE = 'checkboxe'
    TYPE_DELIBERATION = 'tzcld-communities-deliberations'
    TYPE_OTHER_DELIBERATION = 'tzcld-others-communities-deliberations'
    TYPE_CONCILS_DELIBERATION = 'tzcld-councils-departments-deliberations'
    TYPE_OF_FIELD_CHOICES = [
        (TYPE_FALSE, 'Checkboxe'),
        (TYPE_DELIBERATION, 'TZCLD Territory deliberation'),
        (TYPE_OTHER_DELIBERATION, 'TZCLD Other Territory deliberation'),
        (TYPE_CONCILS_DELIBERATION, 'TZCLD Council department deliberation'),
    ]

    name = models.CharField(max_length=1024, blank=True, null=True, default='')
    description = models.CharField(max_length=1024, blank=True, null=True, default='')
    order = models.IntegerField(blank=True, null=True, default=1)
    part = models.ForeignKey(TzcldCommunityEvaluationPointPart, on_delete=models.CASCADE,related_name='part_points', blank=True, null=True)
    points = models.IntegerField(blank=True, null=True, default=0)
    fieldType = models.CharField(
        max_length=125,
        choices=TYPE_OF_FIELD_CHOICES,
        default=TYPE_FALSE,
    )

    def __str__(self):
        try:
            return '{} ({})'.format(self.id, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Evaluation Point')
        verbose_name_plural = _("TZCLD Territories Evaluation Points")

        ordering = ['order']
        container_path = "tzcld-communities-evaluation-points/"
        serializer_fields = ['@id', 'name', 'description', 'order', 'part', 'points', 'fieldType', 'evaluation_point_answer']
        rdf_type = "tzcld:communityEvaluationPoint"
        permission_classes=[ReadOnly|OwnerPermissions]
        depth = 0


#############################
# Page Etat d'avancement => Auto-evaluation => Parties (pointsParts) => Points => Réponse
#############################
class TzcldCommunityEvaluationPointAnswer(Model):
    answer = models.BooleanField(default=False)
    answer_community_deliberation = models.ForeignKey(TzcldCommunityDeliberation, on_delete=models.DO_NOTHING,related_name='community_answer', blank=True, null=True)
    answer_other_community_deliberation = models.ForeignKey(TzcldOtherCommunityDeliberation, on_delete=models.DO_NOTHING,related_name='community_answer', blank=True, null=True)
    answer_concil_department_deliberation = models.ForeignKey(TzcldCouncilDepartmentDeliberation, on_delete=models.DO_NOTHING,related_name='community_answer', blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    evaluation_point = models.ForeignKey(TzcldCommunityEvaluationPoint, on_delete=models.CASCADE,related_name='evaluation_point_answer', blank=True, null=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_answer', blank=True, null=True)
    date =  models.DateField(verbose_name="Date", auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        try:
            return '{} ({})'.format(self.id, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        auto_author = 'author'
        verbose_name = _('TZCLD Territory Evaluation Point Answer')
        verbose_name_plural = _("TZCLD Territories Evaluation Point answers")
        container_path = "tzcld-communities-evaluation-point-answers/"
        serializer_fields = ['@id', 'answer', 'answer_community_deliberation', 'answer_other_community_deliberation', 'answer_concil_department_deliberation', 'comment', 'evaluation_point', 'community', 'date', 'author']
        rdf_type = "tzcld:communityEvaluationPointAnswer"
        permission_classes=[InheritPermissions|RegionalReferentPermissions]
        inherit_permissions = ['community']
        community_path = 'community'
        depth = 0


#############################
# Shared models for user and community
#############################

#############################
# Page d'edition du territoire => Coordonnées et lieux => Téléphones
#############################
class TzcldContactPhone(Model):
    phone = models.CharField(max_length=255, blank=True, null=True, default='')
    phone_type = models.CharField(max_length=255, blank=True, null=True, default='')
    phone_public = models.BooleanField(default=False)
    job = models.ForeignKey(TzcldProfileJob, on_delete=models.CASCADE, related_name='phones', blank=True, null=True)
    location = models.ForeignKey(TzcldTerritoryLocation, on_delete=models.CASCADE, related_name='phones', blank=True, null=True)


    def __str__(self):
        try:
            return '{} ({})'.format(self.position, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Phone')
        verbose_name_plural = _("TZCLD Phones")
        container_path = "tzcld-contact-phone/"
        serializer_fields = ['@id', 'phone', 'phone_type', 'phone_public', 'job', 'location']
        nested_fields = []
        rdf_type = "tzcld:phone"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['job']

#############################
# Page d'edition du territoire => Coordonnées et lieux => Emails
#############################
class TzcldContactEmail(Model):
    email = models.CharField(max_length=255, blank=True, null=True, default='')
    email_type = models.CharField(max_length=255, blank=True, null=True, default='')
    email_public = models.BooleanField(default=False)
    job = models.ForeignKey(TzcldProfileJob, on_delete=models.CASCADE,related_name='emails', blank=True, null=True)
    location = models.ForeignKey(TzcldTerritoryLocation, on_delete=models.CASCADE,related_name='emails', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.position, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Email')
        verbose_name_plural = _("TZCLD Emails")

        container_path = "tzcld-contact-email/"
        serializer_fields = ['@id', 'email', 'email_type', 'email_public', 'job', 'location']
        nested_fields = []
        rdf_type = "tzcld:email"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['job']


#############################
# Page Suivi du territoire => Historique des échanges
#############################
class TzcldTerritoryRequest(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,verbose_name="Interlocuteur")
    date =  models.DateField(verbose_name="Date")
    contactType = models.CharField(max_length=1024, blank=True, null=True, default='',verbose_name="Type of contact")
    subject = models.TextField(blank=True, null=True, verbose_name="Sujet/Demande")
    community = models.ForeignKey(Community, on_delete=models.CASCADE,related_name='tzcld_community_requests', blank=False, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,related_name='territory_request_author')

    def __str__(self):
        try:
            return '{} ({})'.format(self.id, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        auto_author = 'author'
        verbose_name = _('TZCLD Territory Request')
        verbose_name_plural = _("TZCLD Territories Requests")

        container_path = "tzcld-territory-request/"
        serializer_fields = ['@id', 'user', 'date', 'contactType', 'subject', 'community', 'author']
        nested_fields = ['user', 'community']
        rdf_type = "tzcld:territoryRequest"
        permission_classes=[InheritPermissions]
        inherit_permissions = ['community']


#############################
# Page Suivi du territoire => Synthèse
#############################
class TzcldTerritorySynthesisFollowed(Model):
    questions = models.TextField(blank=True, null=True, verbose_name="Questions")
    needs = models.TextField(blank=True, null=True, verbose_name="Needs, Actions")
    targetdate =  models.DateField(verbose_name="Target date", blank=True, null=True)
    community = models.OneToOneField(Community, on_delete=models.CASCADE,related_name='tzcld_community_synthesis_followed', blank=True, null=True)
    date =  models.DateField(verbose_name="Date", auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        try:
            return '{} ({})'.format(self.id, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        auto_author = 'author'
        verbose_name = _('TZCLD Territory Synthesis Followed')
        verbose_name_plural = _("TZCLD Territories Synthesis Followed")

        container_path = "tzcld-territory-synthesis-followed/"
        serializer_fields = ['@id', 'questions', 'needs', 'targetdate', 'community', 'tzcld_referents_community_shared_notes', 'date', 'author', 'tzcld_referents_community_shared_files']
        nested_fields = ['community', 'tzcld_referents_community_shared_notes', 'tzcld_referents_community_shared_files']
        rdf_type = "tzcld:territorySynthesisFollowed"
        permission_classes=[RegionalReferentPermissions]
        community_path = 'community'

#############################
# Page Suivi du territoire => Critères de suiv => Partie
#############################
class TzcldCommunityFollowedPointPart(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    title = models.CharField(max_length=254, blank=True, null=True, default='')
    order = models.IntegerField(blank=True, null=True, default=1)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Followed Point Part')
        verbose_name_plural = _("TZCLD Territories Followed Point Parts")
        
        # authenticated_perms = ['view', 'add']
        # owner_perms = ['inherit', 'change', 'delete']
        # superuser_perms = ['inherit']
        container_path = "tzcld-followed-point-parts/"
        serializer_fields = ['@id', 'name', 'title', 'order', 'followed_part_points']
        ordering = ['order']
        nested_fields = ['followed_part_points']
        rdf_type = "tzcld:followedPointPart"
        depth = 0
        permission_classes=[ReadOnly]

#############################
# Page Suivi du territoire => Critères de suiv => Parties (pointsParts) => Point
#############################
class TzcldCommunityFollowedPoint(Model):

    TYPE_TEXT = 'text'
    TYPE_TEXTAREA = 'textarea'
    TYPE_OF_FIELD_CHOICES = [
        (TYPE_TEXT, 'Text'),
        (TYPE_TEXTAREA, 'Textearea'),
    ]

    name = models.CharField(max_length=1024, blank=True, null=True, default='')
    order = models.IntegerField(blank=True, null=True, default=1)
    part = models.ForeignKey(TzcldCommunityFollowedPointPart, on_delete=models.CASCADE,related_name='followed_part_points', blank=True, null=True)
    fieldType = models.CharField(
        max_length=25,
        choices=TYPE_OF_FIELD_CHOICES,
        default=TYPE_TEXTAREA,
    )
    helpComment = models.TextField(blank=True, null=True, verbose_name="Questions to ask")

    def __str__(self):
        try:
            return '{} ({})'.format(self.id, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Followed Point')
        verbose_name_plural = _("TZCLD Territories Followed Points")
        ordering = ['order']
        container_path = "tzcld-communities-followed-points/"
        serializer_fields = ['@id', 'name', 'order', 'part', 'fieldType', 'helpComment']
        rdf_type = "tzcld:communityFollowedPoint"
        depth = 0
        permission_classes=[ReadOnly]


#############################
# Page Suivi du territoire => Critères de suiv => Parties (pointsParts) => Points => Répnse
#############################
class TzcldCommunityFollowedPointAnswer(Model):
    answer = models.TextField(blank=False, null=True)
    followed_point = models.ForeignKey(TzcldCommunityFollowedPoint, on_delete=models.CASCADE,related_name='followed_point_answer', blank=False, null=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE,related_name='tzcld_community_followed_answer', blank=False, null=True)
    date =  models.DateField(verbose_name="Date", auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        try:
            return '{} ({})'.format(self.id, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        auto_author = 'author'
        verbose_name = _('TZCLD Territory Followed Point Answer')
        verbose_name_plural = _("TZCLD Territories Followed Point answers")
        container_path = "tzcld-communities-followed-point-answers/"
        serializer_fields = ['@id', 'answer', 'followed_point','community', 'date', 'author']
        rdf_type = "tzcld:communityFollowedPointAnswer"
        depth = 0
        permission_classes=[RegionalReferentPermissions]
        community_path = 'community'

#############################
# Page Échanges avec mes référent-es => Notes partagées (via relation community_admins)
# Page Suivi du territoire => Notes partagées (via relation community_referents)
#############################
class TzcldTerritorySharedNote(Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    longdesc = models.TextField(blank=True, null=True)
    community_admins = models.ForeignKey(TzcldCommunityIdentity, on_delete=models.DO_NOTHING,related_name='tzcld_admins_community_shared_notes', blank=True, null=True)
    community_referents = models.ForeignKey(TzcldTerritorySynthesisFollowed, on_delete=models.DO_NOTHING,related_name='tzcld_referents_community_shared_notes', blank=True, null=True)
    conversations = models.ManyToManyField(Conversation, blank=True, related_name='tzcld_shared_notes')
    date =  models.DateField(verbose_name="Date", auto_now=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.id, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        auto_author = 'author'
        owner_field = 'author'
        verbose_name = _('TZCLD Territory Shared Note')
        verbose_name_plural = _("TZCLD Territories Shared Notes")
        container_path = "tzcld-territory-shared-notes/"
        serializer_fields = ['@id', 'author', 'longdesc', 'community_admins', 'community_referents', 'conversations', 'date']
        nested_fields = ['author', 'community_admins', 'community_referents', 'conversations']
        rdf_type = "tzcld:territorySharedNote"
        permission_classes=[ReadAndCreate|OwnerPermissions|RegionalReferentPermissions]
        community_path = 'community_admins.community'


#############################
# Page Échanges avec mes référent-es => Fichiers de suivi (via relation community_admins)
# Page Échanges avec mes référent-es => Partagés avec la grappe (via relation community_referents)
#############################
class TzcldTerritorySharedFile(Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,verbose_name="Interlocuteur")
    name = models.CharField(max_length=1024, blank=True, null=True, default='')
    date =  models.DateField(verbose_name="Date", auto_now=True)
    document = models.URLField(blank=True, null=True, verbose_name="Document")
    community_admins = models.ForeignKey(TzcldCommunityIdentity, on_delete=models.DO_NOTHING,related_name='tzcld_admins_community_shared_files', blank=True, null=True)
    community_referents = models.ForeignKey(TzcldTerritorySynthesisFollowed, on_delete=models.DO_NOTHING,related_name='tzcld_referents_community_shared_files', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        auto_author = 'author'
        owner_field = 'author'
        verbose_name = _('TZCLD Territory Shared File')
        verbose_name_plural = _("TZCLD Territories Shared Files")

        container_path = "tzcld-territory-shared-files/"
        serializer_fields = ['@id', 'author', 'name', 'date', 'document', 'community_admins', 'community_referents']
        nested_fields = ['author', 'community_admins', 'community_referents']
        rdf_type = "tzcld:territorySharedFile"
        permission_classes=[ReadAndCreate|OwnerPermissions|RegionalReferentPermissions]
        community_path = 'community_admins.community'



#############################
# Signals
#############################

# Create tzcld user profile, job instance and contact email/phone when user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_tzcld_profile(sender, instance, created, **kwargs):
    if not Model.is_external(instance) and created:
        tzcld_profile = TzcldProfile.objects.create(user=instance)
        profile_job = TzcldProfileJob.objects.create(profile=tzcld_profile)
        TzcldContactEmail.objects.create(job=profile_job)
        TzcldContactPhone.objects.create(job=profile_job)

        # add the user to the first (tzcld) community
        community = Community.objects.order_by('id').first()
        if community:
            community.members.user_set.add(instance)

# Create tzcld community profile, job instance and contact email/phone when community is created
@receiver(post_save, sender=Community)
def create_tzcld_community(instance, created, **kwargs):
    if not Model.is_external(instance) and created:
        tzCommunity = TzcldCommunity.objects.create(community=instance)
        territory_location = TzcldTerritoryLocation.objects.create(name="Adresse à renseigner", community=tzCommunity)
        TzcldContactEmail.objects.create(email="brad@example.com", location=territory_location)
        TzcldContactPhone.objects.create(phone="0606060606", location=territory_location)

        # create empty community evaluation points answers
        evaluationPoints = TzcldCommunityEvaluationPoint.objects.all()
        for evaluationPoint in evaluationPoints:
            TzcldCommunityEvaluationPointAnswer.objects.create(evaluation_point=evaluationPoint, community=instance)

        # create empty community followed points answers
        followedPoints = TzcldCommunityFollowedPoint.objects.all()
        for followedPoint in followedPoints:
            TzcldCommunityFollowedPointAnswer.objects.create(followed_point=followedPoint, community=instance)

        # create empty TzcldCommunityIdentity instance
        TzcldCommunityIdentity.objects.create(community=instance)

        # create empty TzcldTerritorySynthesisFollowed instance
        TzcldTerritorySynthesisFollowed.objects.create(community=instance)

# Create empty TzcldCommunityEvaluationPointAnswer instance for every existing Territory when TzcldCommunityEvaluationPoint is created
@receiver(post_save, sender=TzcldCommunityEvaluationPoint)
def create_evaluation_point_answers(sender, instance, created, **kwargs):
    if created:
        communities = Community.objects.all()
        for community in communities:
            # Create TzcldCommunityEvaluationPointAnswer
            evaluation_point_answer = TzcldCommunityEvaluationPointAnswer.objects.create(
                community=community,
                evaluation_point=instance
            )

# Create empty TzcldCommunityFollowedPointAnswer instance for every existing Territory when TzcldCommunityFollowedPoint is created
@receiver(post_save, sender=TzcldCommunityFollowedPoint)
def create_followed_point_answers(sender, instance, created, **kwargs):
    if created:
        communities = Community.objects.all()
        for community in communities:
            # Create TzcldCommunityFollowedPointAnswer
            followed_point_answer = TzcldCommunityFollowedPointAnswer.objects.create(
                community=community,
                followed_point=instance
            )